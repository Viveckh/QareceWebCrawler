import os.path
import scrapy
from product_scraper.itemloaders import ProductItemLoader

class ProductsSpider(scrapy.Spider):
    name = 'products-spider'
    handle_httpstatus_list = [301, 302]

    productItemLoader = ProductItemLoader()
    with open(os.path.dirname(__file__) + "/../input/urls.txt", "rt") as f:
        start_urls = [url.strip() for url in f.readlines()]

    def parse(self, response):
        request_url = str(response.request.url).lower()
        
        if 'macys.com' in request_url: 
            loaders = self.productItemLoader.parse_macys(product_url=request_url, html_dump=response)
            for loader in loaders:
                yield loader.item
        elif 'kyliecosmetics.com' in request_url:
            yield self.productItemLoader.parse_kylie_cosmetics(product_url=request_url, html_dump=response)
        elif 'sephora.com' in request_url:
            loaders = self.productItemLoader.parse_sephora(product_url=request_url, html_dump=response)
            for loader in loaders:
                yield loader.item