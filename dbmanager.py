import psycopg2

from config import get_db_params


class DBManager:
    def __init__(self, db_name):
        self.db_name = db_name
        self.params = get_db_params()

    def execute_query(self, query: str):
        """Возвращает сделанный запрос."""
        conn = psycopg2.connect(dbname=self.db_name, **self.params)
        with conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()
        conn.close()

    def get_companies_and_vacancies_count(self):
        """Получает список всех компаний и количество вакансий у каждой компании."""
        query = """
                SELECT employers.name, count(*) as all_vacancies FROM vacancies
                JOIN employers ON vacancies.employer_id = employers.id
                GROUP BY employers.name
                ORDER BY count(*);
                """
        return self.execute_query(query)

    def get_all_vacancies(self):
        """
        Список всех вакансий с указанием названия компании, названия вакансии, зарплаты и ссылки на вакансию,
        отсортированный по убыванию зарплаты "ДО".
        """
        query = """
                SELECT employers.name as employer, vacancies.name as vacancy, vacancies.salary_from, vacancies.salary_to, vacancies.currency, vacancies.url
                FROM vacancies
                JOIN employers ON employers.id = vacancies.employer_id
                ORDER BY vacancies.salary_to DESC
                """
        return self.execute_query(query)

    def get_avg_salary(self):
        """Выводит среднюю зарплату в зарплатах ОТ и ДО, исключая нулевые значения."""
        query = """
                SELECT 'Зарплата "ОТ"' as "Средняя зарплата", ROUND(AVG(salary_from)) as averange_from
                FROM vacancies
                UNION
                SELECT 'Зарплата "ДО"', ROUND(AVG(salary_to)) as averange_to
                FROM vacancies
                WHERE salary_to <> 0
                """
        return self.execute_query(query)

    def get_vacancies_with_higher_salary(self):
        """Выводит вакансии, у которых зп выше средней."""
        query = """
                SELECT *
                FROM vacancies
                WHERE salary_from > (SELECT ROUND(AVG(salary_from))
                                     FROM vacancies
                                     WHERE salary_from <> 0)
                OR salary_to > (SELECT ROUND(AVG(salary_to))
                                FROM vacancies
                                WHERE salary_to <> 0)
               """
        return self.execute_query(query)

    def get_vacancies_with_keyword(self, keyword: str):
        """Выводит вакансии, в названиях которых содержится ключевое слово."""
        formatted_keyword = keyword[1:-1]
        query = f"""
                 SELECT *
                 FROM vacancies
                 WHERE name LIKE '%{formatted_keyword}%'"""
        return self.execute_query(query)
