# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
import re
from jobparser.items import JobparserItem


def format_salary(salary) -> tuple:
    salary = salary.replace('\u202f', '').strip()
    salary_diversity = re.findall(r'\d+', salary)
    if 'от' and 'до' in salary:
        return int(f'{salary_diversity[0]}{salary_diversity[1]}'), int(f'{salary_diversity[2]}{salary_diversity[3]}')
    elif 'от' in salary:
        return int(f'{salary_diversity[0]}{salary_diversity[1]}'), 'з/п не указана'
    else:
        return 'з/п не указана', int(f'{salary_diversity[0]}{salary_diversity[1]}')


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = [
        'https://spb.hh.ru/search/vacancy?area=2&fromSearchLine=true&st=searchVacancy&text=Junior+python+developer']

    def parse(self, response: HtmlResponse):
        next_page = 'https://spb.hh.ru' \
                    + response.css('a[class="bloko-button"][data-qa="pager-next"]').attrib['href']
        print(next_page)
        response.follow(next_page, callback=self.parse)
        vacancy = response.css(
            'div.vacancy-serp div.vacancy-serp-item div.vacancy-serp-item__row_header '
            'a.bloko-link::attr(href)'
        ).extract()
        for link in vacancy:
            yield response.follow(link, callback=self.vacancy_parse)

        if next_page:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)

    def vacancy_parse(self, response: HtmlResponse):
        name = response.css('h1[data-qa="vacancy-title"]::text').getall()[0]
        url = response.url
        salary = ''.join(response.css('span[class="bloko-header-2 bloko-header-2_lite"]::text').getall())
        source = 'HH.ru'
        if salary != 'з/п не указана':
            salary_from, salary_to = format_salary(salary)

        else:
            salary_from, salary_to = 'з/п не указана', 'з/п не указана'

        yield JobparserItem(name=name, url=url, salary_from=salary_from, salary_to=salary_to,
                            source=source)


class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['https://sankt-peterburg.gorodrabot.ru']
    start_urls = [
        'https://sankt-peterburg.gorodrabot.ru/junior_python_developer']

    def parse(self, response: HtmlResponse):
        next_page = response.css('a[class="pager-item pager-item_type_after"]').attrib[
            'href']
        print(next_page)
        response.follow(next_page, callback=self.parse)
        vacancy = response.css(
            'div.result-list__snippet vacancy snippet snippet_clickable div.snippet__inner div.snippet__body '
            'h2.snippet__title a.snippet__title-link link an-vc::attr(href)'
        ).extract()
        for link in vacancy:
            yield response.follow(link, callback=self.vacancy_parse)

        if next_page:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)

    def vacancy_parse(self, response: HtmlResponse):
        name = response.css('h1[class="vacancy-view__title content__title"]::text').getall()[0]
        url = response.url
        salary = ''.join(
            response.css('ul[class="vacancy-view__currency range-list range-list_extend_desktop list"]::text').getall())
        source = 'ГородРабот.ru'
        if salary != 'договорная':
            salary_from, salary_to = format_salary(salary)

        else:
            salary_from, salary_to = 'з/п не указана', 'з/п не указана'

        yield JobparserItem(name=name, url=url, salary_from=salary_from, salary_to=salary_to,
                            source=source)
