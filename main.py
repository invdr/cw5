import pprint

import psycopg2

from config import get_db_params
from utils.db_foo import create_db_and_tables, insert_data
# from dbmanager import DBmanager
from utils.utils import get_vacancies, get_employer_info

DB_NAME = "hh"

company_ids = [
    9498112,  # Yandex
    84585,  # Avito
    1455,  # HeadHunter
    1122462,  # SkyEng
    2180,  # OZON
    78638,  # Tinkoff
    15478,  # VK
    64174,  # 2Gis
    26624,  # Positive Technologies
    834446,  # IT-People
]


def main():
    params = get_db_params()
    create_db_and_tables(DB_NAME, params)

    # составляем список с данными работодателя
    employer_list = [get_employer_info(co_id) for co_id in company_ids]

    # список вакансий всех работодателей
    vacancies = []

    conn = psycopg2.connect(dbname=DB_NAME, **params)
    with conn.cursor() as cur:
        # запись данных компаний в таблицу
        insert_data(cur, 'employer', employer_list)
        conn.commit()

        # вакансии работодателя
        for employer_id in company_ids:
            vacancies.append(get_vacancies(employer_id))

        # запись вакансий в таблицу
        insert_data(cur, 'vacancies', vacancies)
        conn.commit()

    conn.close()

if __name__ == '__main__':
    main()