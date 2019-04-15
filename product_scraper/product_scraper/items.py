# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from product_scraper.utilities import clean_text, to_int, to_float

class ProductScraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class Product(scrapy.Item):
    fields_to_export = ['product_url', 'store', 'product_id', 'sku', 'name', 'brand', 'description', 'picture_urls', 'category', 'weight', \
        'profit_margin_rate', 'original_price_in_usd', 'estimated_shipping_cost_in_usd', 'estimated_profit_in_usd', 'final_price_in_usd', 'final_price_in_npr']
    product_url = scrapy.Field()
    product_id = scrapy.Field()
    sku = scrapy.Field(
        output_processor=clean_text
    )
    parent_sku = scrapy.Field(
        output_processor=clean_text
    )
    store = scrapy.Field(
        output_processor=clean_text
    )
    name = scrapy.Field()
    brand = scrapy.Field()
    description = scrapy.Field()
    short_description = scrapy.Field()
    category = scrapy.Field()
    weight = scrapy.Field(
        output_processor=to_float
    )
    profit_margin_rate =  scrapy.Field(
        output_processor=to_float
    )   
    original_price_in_usd = scrapy.Field(
        output_processor=to_float
    )
    estimated_shipping_cost_in_usd = scrapy.Field(
        output_processor=to_float
    )
    estimated_profit_in_usd = scrapy.Field(
        output_processor=to_float
    )
    final_price_in_usd = scrapy.Field(
        output_processor=to_float
    )
    final_price_in_npr = scrapy.Field(
        output_processor=to_int
    )
    picture_urls = scrapy.Field()
    tax_status = scrapy.Field()
    in_stock = scrapy.Field(
        output_processor=to_int
    )
    backorders_allowed = scrapy.Field(
        output_processor=to_int
    )
    attribute1_name = scrapy.Field()
    attribute1_values = scrapy.Field()
    attribute1_visible = scrapy.Field()
    attribute1_global = scrapy.Field()
    attribute1_default = scrapy.Field()
    attribute2_name = scrapy.Field()
    attribute2_values = scrapy.Field()
    attribute2_visible = scrapy.Field()
    attribute2_global = scrapy.Field()
    attribute2_default = scrapy.Field()
    attribute3_name = scrapy.Field()
    attribute3_values = scrapy.Field()
    attribute3_visible = scrapy.Field()
    attribute3_global = scrapy.Field()
    attribute3_default = scrapy.Field()
    wp_product_type = scrapy.Field()
    wp_published = scrapy.Field(
        output_processor=to_int
    )
    wp_featured = scrapy.Field(
        output_processor=to_int
    )
    wp_visibility = scrapy.Field()
    wp_sold_individually = scrapy.Field(
        output_processor=to_int
    )
    
