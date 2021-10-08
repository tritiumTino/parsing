from __future__ import annotations
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

VACANCY = 'Junior+python+developer'
URL = 'https://spb.hh.ru/search/vacancy?area=2&fromSearchLine=true&st=searchVacancy&text={vacancy}&page={page}'
headers = requests.utils.default_headers()
headers.update({'User-Agent': 'Chrome/94.0.4606.61'})


def format_salary(salary: bs4.element.ResultSet) -> tuple:
    salary = salary.span.text
    salary = salary.replace('\u202f', '').strip()
    salary_diversity = re.findall(r'\d+', salary)
    salary_units = salary[-4:].strip()
    if 'от' in salary:
        return f'{salary_diversity[0]} {salary_units}', 'з/п не указана'
    if 'до' in salary:
        return 'з/п не указана', f'{salary_diversity[0]} {salary_units}'
    return f'{salary_diversity[0]} {salary_units}', f'{salary_diversity[1]} {salary_units}'


def get_salary(vacancy: bs4.element.ResultSet, data: dict) -> None:
    salary = vacancy.find('div', class_='vacancy-serp-item__sidebar')
    if salary and salary.span:
        salary_from, salary_to = format_salary(salary)
        data['salary_from'].append(salary_from)
        data['salary_to'].append(salary_to)
    else:
        data['salary_from'].append('з/п не указана')
        data['salary_to'].append('з/п не указана')


def add_vacancy_data(vacancies: bs4.element.ResultSet, data: dict) -> None:
    for vacancy in vacancies:
        data['name'].append(vacancy.find('a', class_='bloko-link').string)
        data['slug'].append(vacancy.find('a', class_='bloko-link').get('href'))
        get_salary(vacancy, data)
    return None


def pars_html(response: requests.models.Response) -> bs4.element.ResultSet:
    page = BeautifulSoup(response.text, 'lxml')
    return page.findAll('div', class_='vacancy-serp-item')


def save_data(data: dict) -> None:
    df = pd.DataFrame(data=data, columns=['name', 'slug', 'salary_from', 'salary_to'])
    df.to_csv('vacancies.csv', sep='\t', encoding='utf-8')
    return None


def main(pages_count: int) -> None:
    data = {
        'name': [],
        'slug': [],
        'salary_from': [],
        'salary_to': []
            }

    for i in range(pages_count):
        response = requests.get(URL.format(vacancy=VACANCY, page=i), headers=headers)
        vacancies = pars_html(response)
        add_vacancy_data(vacancies, data)

    save_data(data)
    return None


if __name__ == '__main__':
    main(3)
