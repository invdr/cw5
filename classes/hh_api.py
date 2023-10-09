import pprint

import requests


class HH_Api:

    def __init__(self):
        self.url = "https://api.hh.ru"

    def get_employer_info(self, employer_id: int):
        """Method takes information about employer and returns as a dict"""
        request_url = f"{self.url}employers/{employer_id}"

        response = requests.get(url=request_url)

        if response.status_code == 404:
            raise ValueError(f"Работодатель с id {employer_id} не найден")

        return response.json()


    def get_vacancies(self, employer_id: str) -> list:
        print("Идет процесс сбора вакансий...")

        # проходим в цикле по страницам результата запроса (100 записей на 1 страницу)
        for page in range(0, 1):
            new_data = json.loads(self.__get_page(query, page))

            # проверка на 2000 записей при 100 записях на 1 странице
            # если кол-во страниц результата запроса равно значению "page"
            # выходим из цикла
            if new_data['pages'] == page:
                break

            for vacancy in new_data['items']:
                vacancy_id = int(vacancy["id"])
                name = vacancy["name"]
                salary = self.__get_hh_salary(vacancy)
                vacancy_url = vacancy["alternate_url"]
                description = self.__get_hh_description(vacancy)
                vacancy = Vacancy(vacancy_id, name, salary, vacancy_url, description)

                self.collected_vacancies.append(vacancy)

        return self.collected_vacancies

    def get_page(self, employer_id: str, page: int) -> str:
        """Функция получает данные по вакансиям с необходимой страницы для дальнейшей работы."""

        request_url = f"{self.url}/vacancies"
        params = {
            "employer_id": employer_id,
            "page": page,
            "per_page": 100,
            "only_with_salary": True,
        }

        req = requests.get('https://api.hh.ru/vacancies', params)
        data = req.content.decode()  # декодируем
        return data


if __name__ == '__main__':
    api = HH_Api()
    pprint.pp(api.get_employer_info(9498112))