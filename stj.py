import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.common.keys import Keys
from mongo import jurisprudencias
from selenium.webdriver.support.ui import Select
import re
from common import create_data_range



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
    select = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "qtdDocsPagina")))
    select = Select(select)
    select.select_by_index(2)

    return driver




def get_page(driver):
    listadocumentos = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "listadocumentos")))
    soup = BeautifulSoup(listadocumentos.get_attribute('innerHTML'), 'html.parser')
    documentos = soup.find_all('div', class_='documento')
    for documento in documentos:
        doc_textos = documento.find_all('div', class_='docTexto')
        soup_texto = BeautifulSoup(doc_textos[0].__str__().replace("<br/>", "\n"), 'html.parser')
        numero_processo = soup_texto.text.strip().split('\n')
        numero_processo = str.format("{} - {} - {}", numero_processo[0], numero_processo[1], numero_processo[2])
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
            "numero_processo": numero_processo,
            "relator": relator,
            "classes_assunto": classes_assunto,
            "comarca": comarca,
            "orgao_julgador": orgao_julgador,
            "data_julgamento": data_julgamento,
            "data_publicacao": ementa_str + "\n" + acortado_str
            
            
        }
        

from time import sleep
def scraping_stj(interval):
    driver = get_search_results(interval)
    next_page = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "iconeProximaPagina")))
    try:
        next_page_intatived = driver.find_element(By.CLASS_NAME, "iconeProximaPagina.inativo")
    except:
        next_page_intatived = None
    
    while next_page_intatived is None:
        for document in get_page(driver):
            jurisprudencias.insert_one(document)
            print(str.format("inseriu o processo {}", document["numero_processo"]))    
        old_page = driver.page_source
        next_page.click()
        WebDriverWait(driver, 10).until(EC.url_changes(old_page))
        next_page = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "iconeProximaPagina")))
        try:
            next_page_intatived = driver.find_element(By.CLASS_NAME, "iconeProximaPagina.inativo")
        except:
            next_page_intatived = None
        driver.quit()

    
    
    
def scraping_stj_concurrent(intervals, max_workers=5):
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(scraping_stj, intervals)


        

