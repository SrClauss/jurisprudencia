from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import threading
from selenium.webdriver.common.keys import Keys
from mongo import jurisprudencias
from selenium.webdriver.support.ui import Select
import re
from common import create_data_range
from selenium import webdriver
import undetected_chromedriver as uc
from time import sleep
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_search_results(interval):
    driver = uc.Chrome()
    driver.get("https://processo.stj.jus.br/SCON/")
    pesquisa_avançada = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "idMostrarPesquisaAvancada")))
    pesquisa_avançada.click()
    data_inicial = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "dtde1")))
    data_inicial.send_keys(interval[0])
    data_inicial.send_keys(Keys.ENTER)
    data_final = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "dtde2")))
    data_final.send_keys(interval[1])
    data_final.send_keys(Keys.ENTER)
    ActionChains(driver).send_keys(Keys.ENTER).perform()
    return driver




def get_page(driver):
    listadocumentos = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "listadocumentos")))
    soup = BeautifulSoup(listadocumentos.get_attribute('innerHTML'), 'html.parser')
    documentos = soup.find_all('div', class_='documento')
    for documento in documentos:
        doc_textos = documento.find_all('div', class_='docTexto')
        soup_texto = BeautifulSoup(doc_textos[0].__str__().replace("<br/>", "\n"), 'html.parser')
        numero_processo = soup_texto.text.strip().split('\n')
        numero_processo =  numero_processo[2].strip()
        relator = doc_textos[1].text.strip()
        comarca = None
        orgao_julgador = doc_textos[2].text.strip()
        data_julgamento = doc_textos[3].text.strip()
        try:
            data_publicacao = re.findall(r'\d{2}/\d{2}/\d{4}', doc_textos[4].text.strip())[0]
        except:
            data_publicacao = data_julgamento
            
        ementa = doc_textos[5]
        classes_assunto = BeautifulSoup(ementa.__str__().split('<br/>')[0], 'html.parser').text.strip().replace(". ", " / ")
        ementa_str = ementa.text.strip()
        acortado_str = doc_textos[6].text.strip()
        yield {
            "numero_peticao": numero_processo,
            "relator": relator,
            "classes_assunto": classes_assunto,
            "comarca": comarca,
            "orgao_julgador": orgao_julgador,
            "data_julgamento": data_julgamento,
            "data_publicacao": ementa_str + "\n" + acortado_str
            
            
        }
        


def scraping_stj(interval, driver=None):
    
    if driver is None:
        driver = get_search_results(interval)
    
    with driver:
        try:
            erro_mensagem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "erroMensagem")))
            return
        except:
            select = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "qtdDocsPagina")))
            select = Select(select)
            select.select_by_index(2)
            contagem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.col-auto.clsNumDocumento")))
            contagem_inicial = contagem.text.split(" de ")[0]
            contagem_final = int(contagem.text.split(" de ")[1])
            for i in range (51, contagem_final, 50):
                url = driver.current_url
                driver.execute_script(f"navegaForm({i});")
                for element in get_page(driver):
                    jurisprudencias.insert_one(element)
                    print(f"Processo {element['numero_processo']} inserido no banco de dados com sucesso")
                while driver.find_element(By.CSS_SELECTOR, "div.col-auto.clsNumDocumento").text.split(" de ")[0] == contagem_inicial:
                    sleep(1)
                contagem_inicial = driver.find_element(By.CSS_SELECTOR, "div.col-auto.clsNumDocumento").text.split(" de ")[0]
                print(f"{contagem_inicial} processos de {contagem_final} na thread do intervalo {interval}") 
        driver.quit()
    
def get_multi_results(intervals):
    for interval in intervals:
        yield get_search_results(interval)
        
        
        
def scraping_stj_multi(intervals):
    drivers = list(get_multi_results(intervals))
    with ThreadPoolExecutor(max_workers=intervals.__len__()) as executor:
        futures = [executor.submit(scraping_stj, interval, driver) for interval, driver in zip(intervals, drivers)]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(e)
    