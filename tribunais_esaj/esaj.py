from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import time
from common import CRITERIOS_120
from mongo import jurisprudencias, logs, pages
from datetime import datetime




def next_page(driver, timeout=None):
    try:

        next_page = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//a[contains(text(), '>')]")))
        next_page.click()
        if timeout:
            time.sleep(timeout)
        return 1
    except TimeoutException:

        print("Encerrando o Tribunal...")
        return 2
    except StaleElementReferenceException:

        print("StaleElementReferenceException occurred")
        time.sleep(1)
        driver.refresh()
        logs.insert_one({"error": "StaleElementReferenceException occurred", "date": time.strftime("%d/%m/%Y %H:%M:%S")})
        return next_page()
    except Exception as e:
        print(f"Erro inesperado: {e}")
        logs.insert_one({"error": f"Erro inesperado: {e}", "date": time.strftime("%d/%m/%Y %H:%M:%S")})
        driver.refresh()
        return next_page()
    

def get_page(driver, tribunal):
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//tr[@class='fundocinza1']")))
    soup = BeautifulSoup(driver.page_source, "html.parser")
    fundocinza1 = soup.find_all("tr", {"class":"fundocinza1"})
    for tr in fundocinza1:
        numero_peticao = tr.find("tr", {"class":"ementaClass"}).find("td").find("a").text.strip()
        ementaClass2 = tr.find_all("tr", {"class":"ementaClass2"})
        try:
            classe_assunto = ementaClass2[0].find("td").text.strip().replace("\n", "").replace("\t", "").split(":")
            relator = ementaClass2[1].find("td").text.strip().replace("\n", "").replace("\t", "").split(":")
            comarca = ementaClass2[2].find("td").text.strip().replace("\n", "").replace("\t", "").split(":")
            orgao_julgador = ementaClass2[3].find("td").text.strip().replace("\n", "").replace("\t", "").split(":")
            data_julgamento = ementaClass2[4].find("td").text.strip().replace("\n", "").replace("\t", "").split(":")
            data_publicacao = ementaClass2[5].find("td").text.strip().replace("\n", "").replace("\t", "").split(":")
            ementa = ementaClass2[6].find("td").text.strip().replace("\n", "").replace("\t", "")
        except IndexError:
            continue
            
        yield{
            
            "numero_peticao": numero_peticao,
            "classes_assunto": classe_assunto[1].strip(),
            "tribunal": tribunal, 
            "relator": relator[1].strip(),
            "comarca": comarca[1].strip(),
            "orgao_julgador": orgao_julgador[1].strip(),
            "data_julgamento": datetime.strptime(data_julgamento[1].strip(), "%d/%m/%Y"),
            "data_publicacao": datetime.strptime(data_publicacao[1].strip(), "%d/%m/%Y"),
            "ementa": ementa.lstrip("Ementa:").strip()
            
        }
        print(f"Petição: {numero_peticao} coletada com sucesso")
        

    
 



def colect_data(driver, data_inicio,  data_final,tribunal, key=None, timeout=None):
    """
    Função que coleta dados de um site com sistema esaj utilizando um driver do Selenium.

    Parâmetros:
    - driver: objeto do Selenium WebDriver utilizado para interagir com o site.
    - data_inicio: data de início para filtrar os resultados da busca.
    - data_final: data final para filtrar os resultados da busca.
    - tribunal: nome do tribunal para filtrar os resultados da busca.
    - key (opcional): palavra-chave para filtrar os resultados da busca.
    - timeout (opcional): tempo mínimo de espera para a mudança de paginas.

    Retorna:
    - Um gerador que produz registros obtidos da página.

    Exemplo de uso:
    driver = webdriver.Chrome()
    registros = colect_data(driver, '01/01/2022', '31/01/2022', 'Tribunal X', key='palavra-chave', timeout=10)
    for registro in registros:
        print(registro)
    driver.quit()
    """
    
    if key:
        input_ementa = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "iddados.buscaEmenta")))
        input_ementa.send_keys(key)
    input_inicio = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "dtPublicacaoInicio"))).find_element(By.TAG_NAME, "input")
    input_inicio.send_keys(data_inicio)

    input_final = driver.find_element(By.ID, "dtPublicacaoFim").find_element(
        By.TAG_NAME, "input"
    )
    input_final.send_keys(data_final)
    button_submit = driver.find_element(By.XPATH, "//input[@type='submit']")
    button_submit.click()
    numero = driver.find_element(By.ID, "nomeAba-A").text.replace("Acórdãos(", "").replace(")", "")
    print(f"Numero de acórdãos: {numero}")
    pages.insert_one({"key": key if key !=None else "", "data_inicio": data_inicio, "data_final": data_final, "numero": int(numero)})
    while next_page(driver, timeout=timeout) == 1:
        for register in get_page(driver, tribunal):
            yield register
    driver.quit()
    
def multithread_scraping_esaj(tribunal, tipo_range, headless=False, has_key=False, workers=4, keys=CRITERIOS_120, timeout=None):
    """
    Raspa dados simultaneamente de uma URL de tribunal fornecida usando várias threads.

    Args:
    
        tribunal(Tuple[str, str]): Uma tupla contendo o nome do tribunal e a URL do tribunal.
        tipo_range (list): Uma lista de intervalos para processar.
        headless (bool, opcional): Se deve executar o driver do Chrome no modo headless. O padrão é False.
        has_key (bool, opcional): Se deve usar chaves para raspagem. O padrão é False.
        workers (int, opcional): O número de threads de trabalhadores a serem usados. O padrão é 4.
        keys (list, opcional): Uma lista de chaves a serem usadas para raspagem. O padrão é CRITERIOS_120.
        timeout (int, opcional): O valor de tempo limite para cada solicitação, uso esta opção para o estado o tribunal do estado
        de são paulo que bloqueia a raspagem quando as paginas são mudadas com intervalo menor que 0.8 milissegundos. O padrão é None.

    Retorna:
        None
    """
    def process_range_and_key(range, key=None):
        try:
            driver_options = Options()
            if headless:
                driver_options.add_argument("--headless")
            driver = Chrome(driver_options)
            driver.get(tribunal[1])
            for data in colect_data(driver, range[0], range[1], tribunal[0], key, timeout=timeout):
                jurisprudencias.insert_one(data)
        except Exception as e:
            logs.insert_one({"error": str(e), "range": range, "key": key})
        
    with ThreadPoolExecutor(max_workers=workers) as executor:
        for range in tipo_range:
            if has_key:
                for key in keys:
                    executor.submit(process_range_and_key, range, key)
            else:
                executor.submit(process_range_and_key, range)

