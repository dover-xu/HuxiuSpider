# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ZhihuItem(scrapy.Item):
    name = scrapy.Field()
    sex = scrapy.Field()
    description = scrapy.Field()
    city = scrapy.Field()
    profession = scrapy.Field()
    profession_experience = scrapy.Field()
    education_experience = scrapy.Field()
    profile = scrapy.Field()
    answers = scrapy.Field()
    asks = scrapy.Field()
