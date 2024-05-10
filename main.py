from tribunais_esaj.esaj import multithread_scraping_esaj, colect_data
from common import tribunais_esaj, create_data_range
from concurrent.futures import ThreadPoolExecutor, as_completed
from mongo import remove_duplicates, jurisprudencias, completados
from datetime import datetime
from selenium.webdriver import Chrome, ChromeOptions
from tribunais_superiores.stj import scraping_stj, get_search_results, scraping_stj_multi
import undetected_chromedriver as uc




def scraping_stjs():
    
    stjs = [
        lambda: scraping_stj(("01/01/2023", "15/01/2023")),
        lambda: scraping_stj(("16/01/2023", "31/01/2023")),
        lambda: scraping_stj(("01/02/2023", "15/02/2023")),
        lambda: scraping_stj(("16/02/2023", "28/02/2023")),
        lambda: scraping_stj(("01/03/2023", "15/03/2023")),
        lambda: scraping_stj(("16/03/2023", "31/03/2023")),
        lambda: scraping_stj(("01/04/2023", "15/04/2023")),
        lambda: scraping_stj(("16/04/2023", "30/04/2023")),
        lambda: scraping_stj(("01/05/2023", "15/05/2023")),
        lambda: scraping_stj(("16/05/2023", "31/05/2023")),
        lambda: scraping_stj(("01/06/2023", "15/06/2023")),
        lambda: scraping_stj(("16/06/2023", "30/06/2023")),
        lambda: scraping_stj(("01/07/2023", "15/07/2023")),
        lambda: scraping_stj(("16/07/2023", "31/07/2023")),
        lambda: scraping_stj(("01/08/2023", "15/08/2023")),
        lambda: scraping_stj(("16/08/2023", "31/08/2023")),
        lambda: scraping_stj(("01/09/2023", "15/09/2023")),
        lambda: scraping_stj(("16/09/2023", "30/09/2023")),
        lambda: scraping_stj(("01/10/2023", "15/10/2023")),
        lambda: scraping_stj(("16/10/2023", "31/10/2023")),
        lambda: scraping_stj(("01/11/2023", "15/11/2023")),
        lambda: scraping_stj(("16/11/2023", "30/11/2023")),
        lambda: scraping_stj(("01/12/2023", "15/12/2023")),
        lambda: scraping_stj(("16/12/2023", "31/12/2023")),
        lambda: scraping_stj(("01/01/2024", "15/01/2024")),
        lambda: scraping_stj(("16/01/2024", "31/01/2024")),
        lambda: scraping_stj(("01/02/2024", "15/02/2024")),
        lambda: scraping_stj(("16/02/2024", "29/02/2024")),
        lambda: scraping_stj(("01/03/2024", "15/03/2024")),
        lambda: scraping_stj(("16/03/2024", "31/03/2024")),
        lambda: scraping_stj(("01/04/2024", "15/04/2024")),
        lambda: scraping_stj(("16/04/2024", "30/04/2024")),
        lambda: scraping_stj(("01/05/2024", "15/05/2024"))]
    
    with ThreadPoolExecutor(max_workers=1) as executor:
        for tribunal in stjs:
            executor.submit(tribunal)
        

ac = lambda:multithread_scraping_esaj(tribunais_esaj["AC"], create_data_range("01/01/2023", "09/05/2024", 60), headless=False, has_key=False, workers=1, timeout=1.0)
al = lambda:multithread_scraping_esaj(tribunais_esaj["AL"], create_data_range("01/01/2023", "09/05/2024", 15), headless=False, has_key=False, workers=1, timeout=1.0)
am = lambda:multithread_scraping_esaj(tribunais_esaj["AM"], create_data_range("01/01/2023", "09/05/2024", 60), headless=False, has_key=False, workers=1, timeout=1.0)
ce = lambda:multithread_scraping_esaj(tribunais_esaj["CE"], create_data_range("01/01/2023", "09/05/2024", 15), headless=False, has_key=False, workers=1, timeout=1.0)
ms = lambda:multithread_scraping_esaj(tribunais_esaj["MS"], create_data_range("01/01/2023", "09/05/2024", 60), headless=False, has_key=False, workers=1, timeout=1.0)
sp = lambda:multithread_scraping_esaj(tribunais_esaj["SP"], create_data_range("01/01/2023", "09/05/2024", 15), headless=False, has_key=False, workers=2, timeout=1.0)
    
with ThreadPoolExecutor(max_workers=7) as executor:
    for tribunal in [ac, al, am, ce, ms, sp]:
        executor.submit(tribunal)
    executor.submit(scraping_stjs)



remove_duplicates()


        
        

