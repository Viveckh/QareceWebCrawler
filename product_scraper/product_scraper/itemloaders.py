from scrapy.loader import ItemLoader
from product_scraper.items import Product
from scrapy.selector import Selector
from product_scraper.utilities import extract_with_css
import re
import json

class ProductItemLoader(ItemLoader):

    #default_output_processor = clean_text

    def parse_macys(self, product_url, html_dump):
        loader = ProductItemLoader(item=Product(), selector=html_dump)

        hxs = Selector(html_dump)
        json_dump = hxs.select('//script[contains(@data-bootstrap, "feature/product")]/text()').extract()[0]
        data = json.loads(json_dump)
        
        loader.add_value('product_url', "https://www.macys.com" + data['product']['identifier']['productUrl'])
        loader.add_value('product_id', 'macys-' + str(data['product']['id']))
        loader.add_value('sku', 'macys-' + str(data['product']['id']))
        loader.add_value('store', 'Macys')
        loader.add_value('name', data['product']['detail']['name'])
        loader.add_value('brand', data['product']['detail']['brand']['name'])
        loader.add_css('description', 'div[data-section="product-details"] div[data-el="product-details"]')
        loader.add_value('regular_price', data['product']['pricing']['price']['tieredPrice'][0]['values'][0]['value'])

        picture_urls = []
        for image in data['product']['imagery']['images']:
            # Appending the query params to the image url is important, without it a low quality version is shown            
            picture_url = data['product']['urlTemplate']['product'] + image['filePath'] + '?op_sharpen=1&wid=1230&hei=1500'
            picture_urls.append(picture_url)
        
        loader.add_value('picture_urls', ','.join(picture_urls))

        categories = []
        for category in data['product']['relationships']['taxonomy']['categories']:
            categories.append(category['name'])
        
        '''
        loader.add_css('name', 'div[data-auto="product-title"] .product-brand-title a::text')
        loader.add_css('brand', 'div[data-auto="product-title"] .product-name::text')
        loader.add_value('description', 'div[data-section="product-details"] div[data-el="product-details"]')
        loader.add_css('regular_price', 'div[data-el="price-details"] div[data-auto="main-price"]')
        '''
        return loader.load_item()

    def parse_kylie_cosmetics(self, product_url, html_dump):
        loader = ProductItemLoader(item=Product(), selector=html_dump)

        title = str(extract_with_css(html_dump, '.product-page #product-right h1[itemprop="name"]::text'))
        name = title.split('|')[0].strip()
        category = title.split('|')[1].strip()

        loader.add_value('product_url', product_url)
        loader.add_value('product_id', 'kyliecosmetics-' + title)
        loader.add_value('sku', 'kyliecosmetics-' + title)
        loader.add_value('store', 'Kylie Cosmetics')
        loader.add_value('name', title)
        loader.add_value('brand', 'Kylie Cosmetics')
        loader.add_css('description', '#product-description .rte.maindescription')
        loader.add_value('regular_price', float(extract_with_css(html_dump, '#product-description meta[itemprop="price"]::attr("content")')))

        picture_urls = []
        for image in html_dump.css('#thumbnail-gallery div.slide'):
            picture_url = extract_with_css(image, 'a::attr("href")')
            picture_urls.append('https:' + str(picture_url))

        loader.add_value('picture_urls', ','.join(picture_urls))

        return loader.load_item()
    
    def parse_sephora(self, product_url, html_dump):
        loader = ProductItemLoader(item=Product(), selector=html_dump)

        hxs = Selector(html_dump)
        json_dump = hxs.select('//script[contains(@id, "linkJSON")]/text()').extract()[0]
        data = json.loads(json_dump)

        # Sephora returns a list where one of the indexes contains details about the product
        product = None
        for obj in data:
            if 'RegularProductTop' in obj['class']:
                product = obj['props']['currentProduct']   
                break
        
        if product is not None:
            loader.add_value('product_url', product['fullSiteProductUrl'])
            loader.add_value('product_id', 'sephora-' + str(product['currentSku']['skuId']))
            loader.add_value('sku', 'sephora-' + str(product['currentSku']['skuId']))
            loader.add_value('store', 'Sephora')
            loader.add_value('name', product['displayName'])
            loader.add_value('brand', product['brand']['displayName'])
            loader.add_value('description', product['longDescription'])
            loader.add_value('regular_price', float(str(product['currentSku']['listPrice']).replace('$', '')))

            picture_urls = [ str(product['fullSiteHostName']) + str(product['currentSku']['skuImages']['image1500']) ]
            if 'alternateImages' in product['currentSku']:
                for image in product['currentSku']['alternateImages']:
                    picture_urls.append(str(product['fullSiteHostName']) + str(image['image1500']))
                
            loader.add_value('picture_urls', ','.join(picture_urls))

            categories = self.recursive_sephora_category_builder(product['parentCategory'])
            print(categories)
        return loader.load_item()


    """
        The nested object structure for categories is built from child to parent, with topmost parent being at the leaf node
        Example order of object to recurse: Eye Sets > Eyes > Makeup
        Hence it has to be built in a reverse order, starting from the leaf node.
    """
    def recursive_sephora_category_builder(self, obj):
        # Recursive condition, keep recursing until you get to the base condition
        if 'parentCategory' in obj:
            # The recursive function below would have built the array upto this point, starting from bottom up 
            categories = self.recursive_sephora_category_builder(obj['parentCategory'])
            #print(categories)

            # Add the category name for this level and return, so the chain continues
            categories.append(obj['displayName'])
            return categories
        
        # Base condition, this is hit only when you get to the leaf node without any further parentCategory nodes
        if 'displayName' in obj:
            return [obj['displayName']]



