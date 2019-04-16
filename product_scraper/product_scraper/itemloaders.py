import os.path
from scrapy.loader import ItemLoader
from product_scraper.items import Product
from scrapy.selector import Selector
from product_scraper.utilities import extract_with_css
import re
import json
import pandas as pd
from product_scraper.utilities import roundup_to_hundred

class ProductItemLoader(ItemLoader):

    category_mapping_df = pd.read_excel(io=os.path.dirname(__file__) + '/reference_data/category_mapping.xlsx', index_col=None)
    profit_margin_mapping_df = pd.read_excel(io=os.path.dirname(__file__) + '/reference_data/profit_margin_mapping.xlsx', index_col=None)
    category_mapping_df.fillna(value='', inplace=True)
    profit_margin_mapping_df.fillna(value='', inplace=True)

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

        macys_category_list = []
        for category in data['product']['relationships']['taxonomy']['categories']:
            macys_category_list.append(category['name'])

        original_price_in_usd = float(data['product']['pricing']['price']['tieredPrice'][0]['values'][0]['value'])
        
        category, weight, profit_margin_rate, estimated_shipping_cost_in_usd, estimated_profit_in_usd, final_price_in_usd, final_price_in_npr = self.map_and_calculate(store='Macys', category_list=macys_category_list, original_price_in_usd=original_price_in_usd)
        loader.add_value('category', category)
        loader.add_value('weight', weight)
        loader.add_value('profit_margin_rate', profit_margin_rate)
        loader.add_value('original_price_in_usd', original_price_in_usd)
        loader.add_value('estimated_shipping_cost_in_usd', estimated_shipping_cost_in_usd)
        loader.add_value('estimated_profit_in_usd', estimated_profit_in_usd)
        loader.add_value('final_price_in_usd', final_price_in_usd)
        loader.add_value('final_price_in_npr', final_price_in_npr)

        picture_urls = []
        for image in data['product']['imagery']['images']:
            # Appending the query params to the image url is important, without it a low quality version is shown            
            picture_url = data['product']['urlTemplate']['product'] + image['filePath'] + '?op_sharpen=1&wid=1230&hei=1500'
            picture_urls.append(picture_url)
        
        loader.add_value('picture_urls', ','.join(picture_urls))
    
        return loader.load_item()

    def parse_kylie_cosmetics(self, product_url, html_dump):
        loader = ProductItemLoader(item=Product(), selector=html_dump)

        title = str(extract_with_css(html_dump, '.product-page #product-right h1[itemprop="name"]::text'))
        name = title.split('|')[0].strip()
        kylie_category_list = [title.split('|')[1].strip()]

        loader.add_value('product_url', product_url)
        loader.add_value('product_id', 'kyliecosmetics-' + title)
        loader.add_value('sku', 'kyliecosmetics-' + title)
        loader.add_value('store', 'Kylie Cosmetics')
        loader.add_value('name', title)
        loader.add_value('brand', 'Kylie Cosmetics')
        loader.add_css('description', '#product-description .rte.maindescription')

        original_price_in_usd = float(extract_with_css(html_dump, '#product-description meta[itemprop="price"]::attr("content")'))
        
        category, weight, profit_margin_rate, estimated_shipping_cost_in_usd, estimated_profit_in_usd, final_price_in_usd, final_price_in_npr = self.map_and_calculate(store='Kylie', category_list=kylie_category_list, original_price_in_usd=original_price_in_usd)
        loader.add_value('category', category)
        loader.add_value('weight', weight)
        loader.add_value('profit_margin_rate', profit_margin_rate)
        loader.add_value('original_price_in_usd', original_price_in_usd)
        loader.add_value('estimated_shipping_cost_in_usd', estimated_shipping_cost_in_usd)
        loader.add_value('estimated_profit_in_usd', estimated_profit_in_usd)
        loader.add_value('final_price_in_usd', final_price_in_usd)
        loader.add_value('final_price_in_npr', final_price_in_npr)

        picture_urls = []
        for image in html_dump.css('#thumbnail-gallery div.slide'):
            picture_url = extract_with_css(image, 'a::attr("href")')
            picture_urls.append('https:' + str(picture_url))

        loader.add_value('picture_urls', ','.join(picture_urls))

        return loader.load_item()
    
    def parse_sephora(self, product_url, html_dump):
        loader = []
        #loader.append(ProductItemLoader(item=Product(), selector=html_dump))

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
            shared_product_details = {}
            shared_product_details['product_url'] = product['fullSiteProductUrl']
            shared_product_details['product_id'] = 'sephora-' + str(product['currentSku']['skuId'])
            shared_product_details['sku'] = 'sephora-' + str(product['currentSku']['skuId'])
            shared_product_details['store'] = 'Sephora'
            shared_product_details['name'] = product['displayName']
            shared_product_details['brand'] = product['brand']['displayName']
            shared_product_details['description'] = product['longDescription']
            shared_product_details['short_description'] = product['quickLookDescription']
            shared_product_details['tax_status'] = 'taxable'
            shared_product_details['in_stock'] = 1
            shared_product_details['backorders_allowed'] = 0
            shared_product_details['wp_published'] = 1
            shared_product_details['wp_featured'] = 0
            shared_product_details['wp_visibility'] = 'visible'
            if product['variationType'] != 'None':
                shared_product_details['attributes'] = {}
                shared_product_details['attributes'][product['variationType']] = [obj['variationValue'] for obj in product['regularChildSkus'] if 'variationValue' in obj and obj['variationType'] == product['variationType']]
            """
            loader[0].add_value('product_url', product['fullSiteProductUrl'])
            loader[0].add_value('product_id', 'sephora-' + str(product['currentSku']['skuId']))
            loader[0].add_value('sku', 'sephora-' + str(product['currentSku']['skuId']))
            loader[0].add_value('store', 'Sephora')
            loader[0].add_value('name', product['displayName'])
            loader[0].add_value('brand', product['brand']['displayName'])
            loader[0].add_value('description', product['longDescription'])
            loader[0].add_value('short_description', product['quickLookDescription'])
            """

            sephora_category_list = self.recursive_sephora_category_builder(product['parentCategory'])
            # original_price_in_usd = float(str(product['currentSku']['listPrice']).replace('$', ''))
            
            if 'regularChildSkus' in product:
                is_variable_product = True
            else:
                is_variable_product = False

            loader.append(self.gather_sephora_variation(sku_obj=product['currentSku'], parent_details=shared_product_details, category_list=sephora_category_list, is_parent=True, is_variable=is_variable_product))

            if is_variable_product:
                for child_sku_obj in product['regularChildSkus']:
                    loader.append(self.gather_sephora_variation(sku_obj=child_sku_obj, parent_details=shared_product_details, category_list=sephora_category_list, is_parent=False, is_variable=True))

            """
            category, weight, profit_margin_rate, estimated_shipping_cost_in_usd, estimated_profit_in_usd, final_price_in_usd, final_price_in_npr = self.map_and_calculate(store='Sephora', category_list=sephora_category_list, original_price_in_usd=original_price_in_usd)
            loader[0].add_value('category', category)
            loader[0].add_value('weight', weight)
            loader[0].add_value('profit_margin_rate', profit_margin_rate)
            loader[0].add_value('original_price_in_usd', original_price_in_usd)
            loader[0].add_value('estimated_shipping_cost_in_usd', estimated_shipping_cost_in_usd)
            loader[0].add_value('estimated_profit_in_usd', estimated_profit_in_usd)
            loader[0].add_value('final_price_in_usd', final_price_in_usd)
            loader[0].add_value('final_price_in_npr', final_price_in_npr)

            picture_urls = [ str(product['fullSiteHostName']) + str(product['currentSku']['skuImages']['image1500']) ]
            if 'alternateImages' in product['currentSku']:
                for image in product['currentSku']['alternateImages']:
                    picture_urls.append(str(product['fullSiteHostName']) + str(image['image1500']))
                
            loader[0].add_value('picture_urls', ','.join(picture_urls))

            """
        #loader[0].load_item()
        return loader

    def gather_sephora_variation(self, sku_obj, parent_details, category_list, is_parent, is_variable):
        loader = ProductItemLoader(item=Product(), selector=sku_obj)

        loader.add_value('product_url', parent_details['product_url'])
        if is_parent:
            loader.add_value('sku', parent_details['sku'])
            loader.add_value('wp_product_type', 'variable' if is_variable else 'simple')

            # Get all the keys of the attributes if it exists
            if 'attributes' in parent_details:
                variation_attributes = list(parent_details['attributes'].keys())

                for index, attribute in enumerate(variation_attributes):
                    field_name_part = 'attribute' + str(index+1)
                    loader.add_value(field_name_part + '_name', attribute)
                    loader.add_value(field_name_part + '_values', ','.join(parent_details['attributes'][attribute]))
                    loader.add_value(field_name_part + '_visible', 1)
                    loader.add_value(field_name_part + '_global', 1)
                    if attribute == sku_obj['variationType']:
                        loader.add_value(field_name_part + '_default', sku_obj['variationValue'])
        else:
            loader.add_value('parent_sku', parent_details['sku'])
            loader.add_value('wp_product_type', 'variation')

        loader.add_value('store', parent_details['store'])
        loader.add_value('name', parent_details['name'])
        loader.add_value('brand', parent_details['brand'])
        loader.add_value('description', parent_details['description'])
        loader.add_value('short_description', parent_details['short_description'])
        loader.add_value('tax_status', parent_details['tax_status'])
        loader.add_value('in_stock', parent_details['in_stock'])
        loader.add_value('backorders_allowed', parent_details['backorders_allowed'])
        loader.add_value('wp_published', parent_details['wp_published'])
        loader.add_value('wp_featured', parent_details['wp_featured'])
        loader.add_value('wp_visibility', parent_details['wp_visibility'])

        original_price_in_usd = float(str(sku_obj['listPrice']).replace('$', ''))

        category, weight, profit_margin_rate, estimated_shipping_cost_in_usd, estimated_profit_in_usd, final_price_in_usd, final_price_in_npr = self.map_and_calculate(store='Sephora', category_list=category_list, original_price_in_usd=original_price_in_usd)
        loader.add_value('category', category)
        loader.add_value('weight', weight)
        loader.add_value('profit_margin_rate', profit_margin_rate)
        loader.add_value('original_price_in_usd', original_price_in_usd)
        loader.add_value('estimated_shipping_cost_in_usd', estimated_shipping_cost_in_usd)
        loader.add_value('estimated_profit_in_usd', estimated_profit_in_usd)
        loader.add_value('final_price_in_usd', final_price_in_usd)
        loader.add_value('final_price_in_npr', final_price_in_npr)

        base_image_url = "https://www.sephora.com"
        picture_urls = [ base_image_url + str(sku_obj['skuImages']['image1500']) ]
        if 'alternateImages' in sku_obj:
            for image in sku_obj['alternateImages']:
                picture_urls.append(base_image_url + str(image['image1500']))
            
        loader.add_value('picture_urls', ','.join(picture_urls))

        # Handle variations
        #loader.add_value('swatch_url', base_image_url + str(sku_obj['smallImage']))

        loader.load_item()
        return loader


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


    def map_and_calculate(self, store, category_list, original_price_in_usd):
        # The max depth of category hierarchy of our partner stores is 4. 
        # So, we pad category_list with empty values up to length 4 (if it is not that length already) to simply filtering
        hierarchy_depth = 4
        padded_category_list = category_list + ([''] * (hierarchy_depth - len(category_list)))
        
        cat_match_df = self.category_mapping_df[(self.category_mapping_df['store'].str.strip().str.lower() == str(store).strip().lower()) & \
                            (self.category_mapping_df['s_category'].str.strip().str.lower() == str(padded_category_list[0]).strip().lower()) & \
                            (self.category_mapping_df['s_subcategory'].str.strip().str.lower() == str(padded_category_list[1]).strip().lower()) & \
                            (self.category_mapping_df['s_subcategory1'].str.strip().str.lower() == str(padded_category_list[2]).strip().lower()) & \
                            (self.category_mapping_df['s_subcategory2'].str.strip().str.lower() == str(padded_category_list[3]).strip().lower())]
        
        if cat_match_df.empty:
            raise Exception("Could not find a qarece mapping in category mapping file for %s store's category hierarchy %s" % (store, padded_category_list))
        
        # Only get the first record if there are multiple matches
        cat_match_df = cat_match_df.iloc[0]

        qarece_category_list = []
        qarece_category_list.append(cat_match_df['q_category'])
        qarece_category_list.append(cat_match_df['q_subcategory'])
        qarece_category_list.append(cat_match_df['q_subcategory1'])
        qarece_category_list.append(cat_match_df['q_subcategory2'])

        # Use the qarece category hierarchy obtained to get associated business rules outlined for items in that category
        bizrules_match_df = self.profit_margin_mapping_df[(self.profit_margin_mapping_df['q_category'].str.strip().str.lower() == str(cat_match_df['q_category']).strip().lower()) & \
                                                                (self.profit_margin_mapping_df['q_subcategory'].str.strip().str.lower() == str(cat_match_df['q_subcategory']).strip().lower()) & \
                                                                (self.profit_margin_mapping_df['q_subcategory1'].str.strip().str.lower() == str(cat_match_df['q_subcategory1']).strip().lower()) & \
                                                                (self.profit_margin_mapping_df['q_subcategory2'].str.strip().str.lower() == str(cat_match_df['q_subcategory2']).strip().lower())]

        if bizrules_match_df.empty:
            raise Exception("Could not find qarece category mapping in profit margin file for hierarchy of %s" % (qarece_category_list))
        
        # There should be only one match, if multiple, then there is an error within the file
        # Calculate final values to return
        item_weight = float(bizrules_match_df['avg_weight'])
        item_profit_margin_rate = .50
        item_estimated_shipping_cost_in_usd = item_weight * 5
        item_estimated_profit_in_usd = original_price_in_usd * item_profit_margin_rate
        item_final_price_in_usd = original_price_in_usd + item_estimated_shipping_cost_in_usd + item_estimated_profit_in_usd
        item_final_price_in_npr = self.usd_to_npr(item_final_price_in_usd)
        item_category_hierarchy = '>'.join(list(filter(None, qarece_category_list))) # Keep only values that are not empty

        return item_category_hierarchy, item_weight, item_profit_margin_rate, item_estimated_shipping_cost_in_usd, item_estimated_profit_in_usd, item_final_price_in_usd, item_final_price_in_npr

    def usd_to_npr(self, usd_price):
        return roundup_to_hundred(float(usd_price) * 112)

