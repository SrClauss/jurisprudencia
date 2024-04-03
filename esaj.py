from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from tinydb import TinyDB
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import time
from concurrent.futures import ThreadPoolExecutor
from common import TRIBUNAIS_ESAJ
from common import RANGE_DATES
import threading
db = TinyDB("db.json")
jurisprudencia = db.table("jurisprudencia")




count = 0

def next_page(driver):
    try:

        next_page = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//a[contains(text(), '>')]")))
        next_page.click()
        return 1
    except TimeoutException:

        print("Encerrando o Tribunal...")
        return 2
    except StaleElementReferenceException:

        print("StaleElementReferenceException occurred")
        time.sleep(1)
        driver.refresh()
        return next_page()

def get_page(driver):
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
            "relator": relator[1].strip(),
            "comarca": comarca[1].strip(),
            "orgao_julgador": orgao_julgador[1].strip(),
            "data_julgamento": data_julgamento[1].strip(),
            "data_publicacao": data_publicacao[1].strip(),
            
            "ementa": ementa.lstrip("Ementa:").strip()
            
        }
        
        global count 
        count += 1
        print(f"{count} registros inserido com sucesso {data_publicacao[1].strip()}")
    


def colect_data(driver, data_inicio, data_final):
    
    input_inicio = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "dtPublicacaoInicio"))).find_element(By.TAG_NAME, "input")
    
    input_inicio.send_keys(data_inicio)



    input_final = driver.find_element(By.ID, "dtPublicacaoFim").find_element(
        By.TAG_NAME, "input"
    )
    input_final.send_keys(data_final)
    button_submit = driver.find_element(By.XPATH, "//input[@type='submit']")
    button_submit.click()
    
    while next_page(driver) == 1:
        for register in get_page(driver):
            yield register
    
    



def raspe_esaj(url):
    list = []
    for range in RANGE_DATES:
        driver_options = Options()
        #driver_options.add_argument("--headless")
        driver = Chrome(driver_options)
        driver.get(url)
 
        for data in colect_data(driver, range[0], range[1]):
            list.append(data) 
        jurisprudencia.insert_multiple(list)
                


def raspe_concorrente():
    with ThreadPoolExecutor() as executor:
        executor.map(raspe_esaj, TRIBUNAIS_ESAJ)
        
if __name__ == "__main__":
    raspe_esaj("https://esaj.tjsp.jus.br/cjsg/resultadoCompleta.do")