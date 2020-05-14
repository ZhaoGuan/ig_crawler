# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class IgCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class IGItem(scrapy.Item):
    user_data = scrapy.Field()
    following = scrapy.Field()
    follower = scrapy.Field()
    level = scrapy.Field()
