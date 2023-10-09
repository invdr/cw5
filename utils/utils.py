import pprint

import psycopg2
import requests

URL = "https://api.hh.ru"


def get_employer_info(employer_id: int):
    """Возвращает информацию о работодателе по его id"""

    request_url = f"{URL}/employers/{employer_id}"

    response = requests.get(url=request_url)
    return response.json()


def get_page(employer_id: str, page: int) -> dict:
    """Функция получает данные по вакансиям с необходимой страницы для дальнейшей работы."""
    request_url = f"{URL}/vacancies"
    params = {
        "employer_id": employer_id,
        "page": page,
        "per_page": 100,
        "only_with_salary": True,
    }

    response = requests.get(url=request_url, params=params)
    return response.json()


def get_vacancies(employer_id):

    vacancies_list = []

    print('Идет процесс сбора вакансий...')
    # проходим в цикле по страницам результата запроса (100 записей на 1 страницу)
    for page in range(0, 1):
        vacancies = get_page(employer_id, page)
        # проверка на 2000 записей при 100 записях на 1 странице
        # если кол-во страниц результата запроса равно значению "page"
        # выходим из цикла

        items = vacancies['items'][0]
        vac_id = items['id']
        name = items['name']
        area = items['area']['name']
        salary_from = items['salary']['from']
        salary_to = items['salary']['to']
        currency = items['salary']['currency']
        vac_url = items['url']
        vacancies_list.extend([items])

    return vacancies_list


def create_database(database_name: str, params: dict) -> None:
    """Создание базы данных и таблиц для сохранения данных о работодателях и вакансиях."""

    # connect to create database
    conn = psycopg2.connect(dbname='postgres', **params)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(f"DROP DATABASE IF EXISTS {database_name}")
    cur.execute(f"CREATE DATABASE {database_name}")

    conn.close()

    # create tables
    conn = psycopg2.connect(dbname=database_name, **params)
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE employers (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL,
                open_vacancies SMALLINT,
                area VARCHAR(50),
                url VARCHAR(100),
                description TEXT
            )
        """
        )

    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE vacancies (
                id SERIAL PRIMARY KEY,
                name VARCHAR NOT NULL,
                employer_id INT REFERENCES employers(id),
                area VARCHAR(50),
                salary_from SMALLINT,
                salary_to SMALLINT,
                currency VARCHAR(3),
                url VARCHAR(100)
            )
        """
        )

    conn.commit()
    conn.close()


if __name__ == '__main__':
    vac = get_vacancies(9498112)
    pprint.pp(vac)
