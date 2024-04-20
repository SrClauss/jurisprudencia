from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import re
import time
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import Select
from mongo import jurisprudencias






def get_page(driver):
    contents = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='content']")))
    for content in contents:
        
        soup = BeautifulSoup(content.get_attribute('outerHTML'), 'html.parser')
        rows_5 = soup.find_all("div", class_="column is-5-tablet is-full-touch")
        rows_7 = soup.find_all("div", class_="column is-7-tablet is-full-touch")
        data_julgamento = datetime.strptime(rows_5[0].text.replace("Data: ", "").strip(),"%d/%b/%Y")
        numero_peticao = rows_5[1].text.replace("Número: ", "").strip()
        classes_assunto = rows_5[2].text.replace("Número: ", "").strip() + " / " + rows_7[2].text.replace("Assunto: ", "").strip()
        orgao_julgador = rows_7[0].text.replace("Órgão julgador: ", "").strip()
        relator = rows_7[1].text.replace("Magistrado: ", "").strip()
        
        ementa = soup.find("div", class_="content is-full has-text-justified")
        comarca = re.search('Juízo de.*? - ', ementa.text.strip())
        if comarca:
            comarca = comarca.group(0).replace("Juízo de ", "").replace(" - ", "").strip()
        else:
            comarca = ""
        dict = {
            "numero_peticao": numero_peticao, 
            "classes_assunto": classes_assunto,
            "relator": relator,
            "comarca":comarca + " - ES",
            "orgao_julgador": orgao_julgador,
            "data_julgamento": data_julgamento,
            "data_publicacao": "",
            "ementa": ementa.text.strip().replace("\n", "").replace("Juízo de " + comarca + " - ", "").strip()
            
            
        }
        
        yield dict

def raspe_tjes():
    driver = Chrome()
    driver.get("https://sistemas.tjes.jus.br/consultas_publicas/busca/pje1g")



    input_criterio = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "input.is-info.is-size-6")))

    input_criterio.send_keys("ESPÍRITO SANTO")
    input_inicial = driver.find_element(By.ID, "datepicker-end")
    input_inicial.send_keys("05012023")
    input_final = driver.find_element(By.ID, "datepicker-start")
    input_final.send_keys("31122023")
    select_ordenacao = Select(driver.find_element(By.ID, "sort_by"))
    select_ordenacao.select_by_index(1)
    button_pesquisar = driver.find_element(By.CLASS_NAME, "button.is-pulled-right.is-info.mt-1")
    button_pesquisar.click()

    paginacao = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "pagination-list")))
    botoes = paginacao.find_elements(By.CLASS_NAME, "pagination-link")
    ultimo_valor = int(botoes[3].get_attribute("value"))
    def press_next(driver, num):
        try:
            return WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, f".pagination-link[value='{num}']")))
        except:
            time.sleep(0.25)
            driver.refresh()
            return press_next(driver, num)
        
        
    for i in range(2, ultimo_valor -1):
        
        button = press_next(driver, i)
        for value in get_page(driver):
            jurisprudencias.insert_one(value)  
        time.sleep(0.25)
        button.click()
