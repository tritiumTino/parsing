import scrapy


class JobparserItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
    salary_from = scrapy.Field()
    salary_to = scrapy.Field()
    source = scrapy.Field()

    pass
