import pprint

import psycopg2

from config import get_db_params
from utils.db_foo import create_db_and_tables, insert_data
from utils.utils import get_vacancies, get_employer_info
from dbmanager import DBManager

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


def fill_database() -> None:
    params = get_db_params()
    create_db_and_tables(DB_NAME, params)

    conn = psycopg2.connect(dbname=DB_NAME, **params)
    with conn.cursor() as cur:
        # запись данных компаний в таблицу
        for emp_id in company_ids:
            emp_data = get_employer_info(emp_id)
            insert_data(cur, 'employers', emp_data)

            # вакансии работодателя
            vacancies = get_vacancies(emp_id)
            for vacancy in vacancies:
                cur.execute(f"""INSERT INTO vacancies
                                VALUES ({', '.join(['%s'] * (len(vacancy) + 1))})""",
                            (vacancy['vac_id'], vacancy['name'], emp_id, vacancy['area'], vacancy['salary_from'],
                             vacancy['salary_to'], vacancy['currency'], vacancy['vac_url'])
                            )

    conn.commit()
    conn.close()


def main():
    fill_database()
    db_manager = DBManager(DB_NAME)
    print(f"База данных {DB_NAME} создана и данные успешно занесены.\n")
    while True:
        print("[1] - Получить список компаний и кол-во вакансий\n"
              "[2] - Все вакансии с данными\n"
              "[3] - Средняя зп по вакансиям\n"
              "[4] - Все вакансии с зарплатой выше средней\n"
              "[5] - Все вакансии, которые содержат поисковые слова\n"
              "[0] - Выход")

        user_choice = int(input("Выберите действие из списка: "))
        if 1 <= user_choice <= 5:
            print("\n********************************")
            if user_choice == 1:
                pprint.pp(db_manager.get_companies_and_vacancies_count())
            elif user_choice == 2:
                pprint.pp(db_manager.get_all_vacancies())
            elif user_choice == 3:
                pprint.pp(db_manager.get_avg_salary())
            elif user_choice == 4:
                pprint.pp(db_manager.get_vacancies_with_higher_salary())
            elif user_choice == 5:
                user_input = input("Введите ключевое слово: ")
                pprint.pp(db_manager.get_vacancies_with_keyword(user_input))
            print("********************************\n")

        elif user_choice == 0:
            quit("Спасибо за все!")
        else:
            print("Введите числовое значение от 0 до 5")


if __name__ == '__main__':
    main()
