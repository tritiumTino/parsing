from __future__ import annotations
import requests
from lxml import html
from pprint import pprint
import re
from pymongo import MongoClient
import time

headers = requests.utils.default_headers()
headers.update({'User-Agent': 'Chrome/94.0.4606.61'})
news_sources = ['https://meduza.io', 'https://yandex.ru/news', 'https://lenta.ru/']


def connect_to_db() -> Collection:
    client = MongoClient('localhost', 27017)
    db = client.news
    collection = db.timeline
    return collection


def check_existence(data: dict, collection: Collection) -> bool:
    post = collection.count_documents({'link': {'$eq': data['link']}})
    if post:
        return True
    return False


def add_news_to_db(data: dict, collection: Collection) -> None:
    if not check_existence(data, collection):
        collection.insert_one(data)
    return None


def update_data(name: str, link: str, date: str, source: str, collection: Collection) -> None:
    data = {
            'name': name,
            'link': link,
            'date': date,
            'source': source
    }
    add_news_to_db(data, collection)
    return None


def pars_meduza(root, link: str, collection: Collection) -> None:
    articles = root.xpath(
        '//article[contains(@class, "SimpleBlock-root")]/div[contains(@class, "SimpleBlock-wrap")]')
    for block in articles:
        name = block.xpath('./div[contains(@class, "SimpleBlock-content")]/h2/a/span/text()')[0]
        part = block.xpath('./div[contains(@class, "SimpleBlock-content")]/h2/a/@href')[0]
        date = block.xpath('./div[contains(@class, "SimpleBlock-footer")]/div/div/time/text()')[0]

        update_data(name, link+part, date, 'Meduza', collection)
    return None


def pars_yandex(root, collection: Collection) -> None:
    articles = root.xpath('//article[contains(@class, "mg-card")]')
    for block in articles:
        namelink = block.xpath('./*/*/*/a | ./*/a | ./*/*/a')[0]
        name = namelink.xpath('./h2/text()')[0].replace('\xa0', ' ')
        link = namelink.xpath('./@href')[0]
        date = block.xpath(
            './*/div[contains(@class, "mg-card-footer")]/*/*/span[contains(@class, "mg-card-source__time")]/text() |'
            './div[contains(@class, "mg-card-footer")]/*/*/span[contains(@class, "mg-card-source__time")]/text()')[0]

        update_data(name, link, date, 'Yandex', collection)
    return None


def pars_lenta(root, link: str, collection: Collection) -> None:
    articles = root.xpath('//section[contains(@class, "js-top-seven")]/div/div[contains(@class, "item")]')
    for block in articles:
        name = block.xpath('./a/text() | ./h2/a/text()')[0]
        href = block.xpath('./a/@href')[0]
        date = block.xpath('./a/time/text() | ./h2/a/time/text()')[0]

        update_data(name, link+href, date, 'Lenta', collection)
    return None


def main() -> None:
    collection = connect_to_db()
    for link in news_sources:
        response = requests.get(link, headers=headers)
        root = html.fromstring(response.text)
        if 'meduza' in link:
            pars_meduza(root, link, collection)
        elif 'yandex' in link:
            pars_yandex(root, collection)
        else:
            pars_lenta(root, link, collection)
    return None


if __name__ == '__main__':
    main()
