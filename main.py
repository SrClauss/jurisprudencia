from tribunais_esaj.esaj import raspe_concurrent, colect_data
from common import tribunais_esaj, create_data_range
from concurrent.futures import ThreadPoolExecutor
from mongo import remove_duplicates, jurisprudencias, pages
from datetime import datetime
from selenium.webdriver import Chrome, ChromeOptions
from stj import scraping_stj_concurrent, get_search_results

if __name__ == "__main__":
    """
    tribunais = ["https://esaj.tjac.jus.br/cjsg/consultaCompleta.do",
                "https://www2.tjal.jus.br/cjsg/consultaCompleta.do",
                "https://consultasaj.tjam.jus.br/cjsg/consultaCompleta.do",
                "https://esaj.tjce.jus.br/cjsg/consultaCompleta.do",
                "https://esaj.tjms.jus.br/cjsg/consultaCompleta.do"]
    
    data_range = create_data_range("01/01/2023", "31/03/2023", 10)
    with ThreadPoolExecutor(max_workers=4) as executor:
        for tribunal in tribunais:
            executor.submit(raspe_concurrent, tribunal, data_range, False, False, 4)
    """
get_search_results(["01/05/2023", "31/05/2023" ])
    