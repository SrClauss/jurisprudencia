from tribunais_esaj.esaj import raspe_concurrent, colect_data
from common import tribunais_esaj, create_data_range
from concurrent.futures import ThreadPoolExecutor, as_completed
from mongo import remove_duplicates, jurisprudencias, pages
from datetime import datetime
from selenium.webdriver import Chrome, ChromeOptions
from tribunais_superiores.stj import scraping_stj, get_search_results, scraping_stj_multi
import undetected_chromedriver as uc
if __name__ == "__main__":
    
    raspe_concurrent(tribunais_esaj["SP"], create_data_range("01/01/2023", "31/01/2023", 15), False, False, 3, timeout=1)
    
    