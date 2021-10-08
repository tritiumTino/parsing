from __future__ import annotations
import requests
from bs4 import BeautifulSoup
import re
from pymongo import MongoClient
import time


VACANCY = 'Junior+python+developer'
URL = 'https://spb.hh.ru/search/vacancy?area=2&fromSearchLine=true&st=searchVacancy&text={vacancy}&page={page}'
headers = requests.utils.default_headers()
headers.update({'User-Agent': 'Chrome/94.0.4606.61'})


def connect_to_db():
    client = MongoClient('localhost', 27017)
    db = client.vacancies
    collection = db.docs
    return collection


def check_existence(data: dict, collection: Collection) -> bool:
    post = collection.count_documents({'slug': {'$eq': data['slug']}})
    if post:
        return True
    return False


def add_vacancy_to_db(data: dict, collection) -> None:
    if not check_existence(data, collection):
        collection.insert_one(data)


def format_salary(salary: bs4.element.ResultSet) -> tuple:
    salary = salary.span.text
    salary = salary.replace('\u202f', '').strip()
    salary_diversity = re.findall(r'\d+', salary)
    salary_units = salary[-4:].strip()
    if 'от' in salary:
        return salary_diversity[0], 0, salary_units
    if 'до' in salary:
        return 0, salary_diversity[0], salary_units
    return salary_diversity[0], salary_diversity[1], salary_units


def get_salary(vacancy: bs4.element.ResultSet, data: dict) -> None:
    salary = vacancy.find('div', class_='vacancy-serp-item__sidebar')
    if salary and salary.span:
        salary_from, salary_to, salary_units = format_salary(salary)
        data['salary_from'] = int(salary_from)
        data['salary_to'] = int(salary_to)
        data['salary_units'] = salary_units
    return None


def add_page_data(vacancies: bs4.element.ResultSet, collection) -> None:
    for vacancy in vacancies:
        data = {
            'name': vacancy.find('a', class_='bloko-link').string,
            'slug': vacancy.find('a', class_='bloko-link').get('href').split('?')[0],
            'salary_from': 0,
            'salary_to': 0,
            'salary_units': ''
        }
        get_salary(vacancy, data)
        add_vacancy_to_db(data, collection)
    return None


def pars_html(response: requests.models.Response) -> bs4.element.ResultSet:
    page = BeautifulSoup(response.text, 'lxml')
    return page.findAll('div', class_='vacancy-serp-item')


def main(pages_count: int):
    collection = connect_to_db()
    while True:
        for i in range(pages_count):
            response = requests.get(URL.format(vacancy=VACANCY, page=i), headers=headers)
            page = pars_html(response)
            add_page_data(page, collection)
        time.sleep(600)


if __name__ == '__main__':
    main(3)
