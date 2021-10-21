import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst
from w3lib.html import remove_tags


def clear_price(price):
    price = price.replace(' ', '')
    if price.isdigit():
        return float(price)


class LeruaparserItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    name = scrapy.Field()
    photos = scrapy.Field()
    price = scrapy.Field(
        input_processor=MapCompose(remove_tags, clear_price),
        output_processor=TakeFirst()
    )
    description = scrapy.Field()
    pass
