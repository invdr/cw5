import psycopg2
from psycopg2 import Error


def create_db_and_tables(database_name: str, params: dict) -> None:
    """Создание базы данных и таблиц для сохранения данных о работодателях и вакансиях."""

    # connect to create database
    conn = psycopg2.connect(dbname="postgres", **params)
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


def insert_data(cur, table: str, data: list) -> None:
    """Запись данных в таблицу."""
    # получаем кол-во %s по кол-ву столбцов в таблице
    values_count = ", ".join(["%s"] * len(data[0]))
    try:
        # получаем данные data в таблицу table
        cur.executemany(f"INSERT INTO {table} VALUES ({values_count})", data)
        # заносим полученные данные в таблицу в pgAdmin
        print(f"Данные успешно внесены в таблицу {table.upper()}")
    except Error as e:
        print(f"Произошла {e}")


