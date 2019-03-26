# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from product_scraper.utilities import clean_text, to_int

class ProductScraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class Product(scrapy.Item):
    product_url = scrapy.Field()
    product_id = scrapy.Field(
        output_processor=to_int
    )
    sku = scrapy.Field(
        output_processor=clean_text
    )
    store = scrapy.Field(
        output_processor=clean_text
    )
    name = scrapy.Field()
    brand = scrapy.Field()
    description = scrapy.Field()
    regular_price = scrapy.Field(
        output_processor=to_int
    )
    picture_urls = scrapy.Field()