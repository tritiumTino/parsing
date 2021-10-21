import scrapy
from scrapy.http import HtmlResponse

from productparser.items import LeruaparserItem


class LeruaSpider(scrapy.Spider):
    name = 'lerua'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, mark):
        self.start_urls = [f'https://leroymerlin.ru/catalogue/{mark}/']

    def parse(self, response: HtmlResponse):
        ads_links = response.xpath(
            '//div[@class="phytpj4_plp largeCard"]/a[@class="bex6mjh_plp b1f5t594_plp iypgduq_plp nf842wf_plp"]'
            '//@href').extract()

        for link in ads_links:
            yield response.follow(link, callback=self.parse_ads)

    def parse_ads(self, response: HtmlResponse):
        name = response.css('h1[class="header-2"]::text').getall()[0]
        photos = response.xpath('//uc-pdp-media-carousel/img//@src').getall()
        price = response.css('span[slot="price"]::text').getall()[0]
        description = '\n'.join(
            response.xpath('//uc-pdp-section-vlimited[@class="section__vlimit"]/div/p/text()').getall())
        print(description)

        yield LeruaparserItem(name=name, photos=photos, price=price, description=description)
