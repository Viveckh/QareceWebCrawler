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
    name = scrapy.Field()
    brand = scrapy.Field()
    description = scrapy.Field()
    marked_price = scrapy.Field()
    sale_price = scrapy.Field(
        output_processor=to_int
    )
    picture_urls = scrapy.Field()