from __future__ import annotations
from pymongo import MongoClient
from hw3_task_1 import connect_to_db


def form_sample(collection: Collection, salary: int, units: str):
    vacancies = collection.find({'salary_from': {'$gt': salary}, 'salary_units': units})
    return vacancies


def main(salary: int, units: str):
    collection = connect_to_db()
    vacancies = form_sample(collection, salary, units)
    for vacancy in vacancies:
        print(vacancy)


if __name__ == '__main__':
    main(60000, 'руб.')
