from tribunais_esaj.esaj import raspe_concurrent
from common import TRIBUNAIS_ESAJ, RANGE_DATES_10
from concurrent.futures import ThreadPoolExecutor
from mongo import remove_duplicates




if __name__ == "__main__":
    raspe_concurrent(TRIBUNAIS_ESAJ[0], RANGE_DATES_10, False, False, 1)
    