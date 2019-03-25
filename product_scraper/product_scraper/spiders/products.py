import os.path
import scrapy
from product_scraper.itemloaders import ProductItemLoader

def extract_with_css(response, query):
    return response.css(query).get(default='').strip()

class ProductsSpider(scrapy.Spider):
    name = 'products-spider'

    with open(os.path.dirname(__file__) + "/../input/urls.txt", "rt") as f:
        start_urls = [url.strip() for url in f.readlines()]

    def parse(self, response):
        request_url = str(response.request.url).lower()
        
        if 'macys.com' in request_url: 
            yield ProductItemLoader.parse_macys(self, product_url=request_url, html_dump=response)
        elif 'kyliecosmetics.com' in request_url:
            yield ProductItemLoader.parse_kylie_cosmetics(self, product_url=request_url, html_dump=response)