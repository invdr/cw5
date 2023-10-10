import pprint

import requests
import re

URL = "https://api.hh.ru"


def delete_html_tags(description: str) -> str:
    res = re.sub(r"\<[^>]*\>", "", description)
    res = res.replace("&mdash;", "-")
    res = res.replace("\xa0", "")
    res = res.replace("\n", "")
    res = res.replace("\t", " ")
    res = res.replace("\r", "")
    res = res.replace("&nbsp;", " ")
    return res


def get_employer_info(employer_id: int) -> tuple:
    """Возвращает информацию о работодателе по его id"""

    request_url = f"{URL}/employers/{employer_id}"

    employer_response = requests.get(url=request_url).json()
    emp_id = employer_response["id"]
    emp_name = employer_response["name"]
    emp_area = employer_response["area"]["name"]
    emp_url = employer_response["alternate_url"]
    emp_description = delete_html_tags(employer_response["description"])
    employer_info = (emp_id, emp_name, emp_area, emp_url, emp_description)

    return employer_info


def get_page(employer_id: int, page: int) -> dict:
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


def get_vacancies(employer_id: int) -> list[dict]:
    start_page = get_page(employer_id, 0)
    pages_number = start_page["pages"]

    vacancies_list = []

    # проходим в цикле по страницам результата запроса (100 записей на 1 страницу)
    for page in range(0, pages_number):
        vacancies = get_page(employer_id, page)

        # проверка на 2000 записей при 100 записях на 1 странице
        for vacancy in vacancies['items']:
            vac_info = {
                'vac_id': vacancy["id"],
                'name': vacancy["name"],
                'area': vacancy["area"]["name"],
                'salary_from': (
                    vacancy["salary"]["from"] if vacancy["salary"]["from"] else 0
                ),
                'salary_to': vacancy["salary"]["to"] if vacancy["salary"]["to"] else 0,
                'currency': vacancy["salary"]["currency"],
                'vac_url': vacancy["url"],
            }
            vacancies_list.append(vac_info)

    return vacancies_list


if __name__ == "__main__":
    vac = get_vacancies(9498112)
    pprint.pp(vac)
