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

    f_category_mapping_errors = open(os.path.dirname(__file__) + "/output/category_mapping_errors.csv", "a")
    f_profit_mapping_errors = open(os.path.dirname(__file__) + "/output/profit_mapping_errors.csv", "a")

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

    def parse_macys(self, product_url, html_dump):
        loaders = []

        hxs = Selector(html_dump)
        json_dump = hxs.select('//script[contains(@data-bootstrap, "feature/product")]/text()').extract()[0]
        data = json.loads(json_dump)

        # Pretty much all the info we need is within the product node, so lets take that
        product = data['product']

        if product is not None:
            shared_product_details = {}
            shared_product_details['product_url'] = "https://www.macys.com" + product['identifier']['productUrl']
            shared_product_details['product_id'] = 'macys-' + str(product['id'])
            shared_product_details['sku'] = 'macys-' + str(product['id'])
            shared_product_details['store'] = 'Macys'
            shared_product_details['name'] = product['detail']['name']
            shared_product_details['brand'] = product['detail']['brand']['name']
            shared_product_details['description'] = '<p>' + product['detail']['description'] + '</p>' + (('<ul><li>' + '</li><li>'.join(list(product['detail']['bulletText'])) + '</li><ul>') if 'bulletText' in product['detail'] else '')
            shared_product_details['short_description'] = product['detail']['description']
            shared_product_details['tax_status'] = 'taxable'
            shared_product_details['in_stock'] = 1
            shared_product_details['backorders_allowed'] = 0
            shared_product_details['wp_published'] = 1
            shared_product_details['wp_featured'] = 0
            shared_product_details['wp_visibility'] = 'visible'
            shared_product_details['base_image_urls'] = product['urlTemplate']
            if 'upcs' in product['relationships']:
                upcs_list = dict(product['relationships']['upcs']).keys()
            else:
                upcs_list = dict(product['relationships']['memberProductMap']).keys()
            if len(upcs_list) > 1:
                is_variable_product = True
                shared_product_details['attributes'] = {}
                # Extract all keys from the traits node, exclude keys that are only a mapping and not an attribute
                temp_valid_attrs = list(filter(lambda val: val != 'traitsMaps', dict(product['traits']).keys()))
                shared_product_details['attributes_list'] = temp_valid_attrs
                for attr in temp_valid_attrs:
                    shared_product_details['attributes'][attr] = product['traits'][attr]
            else:
                is_variable_product = False
            
            # Retrieve categories
            macys_category_list = []
            for category in data['product']['relationships']['taxonomy']['categories']:
                macys_category_list.append(category['name'])

            # The price will be the same for all variations of a product
            prices = [float(obj['value']) for obj in data['product']['pricing']['price']['tieredPrice'][0]['values']]
            shared_product_details['original_price_in_usd'] = max(prices)
            
            loaders.append(self.gather_macys_variation(sku_obj=product, parent_details=shared_product_details, category_list=macys_category_list, is_parent=True, is_variable=is_variable_product))

            if is_variable_product:
                for upcs in upcs_list:
                    if 'upcs' in product['relationships']:
                        child_sku_obj = product['relationships']['upcs'][upcs]
                    else:
                        child_sku_obj = product['relationships']['memberProductMap'][upcs]
                    loaders.append(self.gather_macys_variation(sku_obj=child_sku_obj, parent_details=shared_product_details, category_list=macys_category_list, is_parent=False, is_variable=True))

        return loaders


    def gather_macys_variation(self, sku_obj, parent_details, category_list, is_parent, is_variable):
        loader = ProductItemLoader(item=Product(), selector=sku_obj)

        base_image_url = parent_details['base_image_urls']['product']
        picture_urls = []
        variation_attributes = parent_details.get('attributes_list', [])

        loader.add_value('product_url', parent_details['product_url'])
        if is_parent:
            loader.add_value('sku', parent_details['sku'])
            loader.add_value('wp_product_type', 'variable' if is_variable else 'simple')
            loader.add_value('description', parent_details['description'])
            loader.add_value('short_description', parent_details['short_description'])

            for image in sku_obj['imagery']['images']:
                picture_urls.append(base_image_url + str(image['filePath']) + '?op_sharpen=1&wid=1230&hei=1500')

            # Get all the keys of the attributes if it exists and fill the attribute details for parent (which includes all possible values)
            if 'attributes' in parent_details:
                for index, attribute in enumerate(variation_attributes):
                    field_name_part = 'attribute' + str(index+1)
                    loader.add_value(field_name_part + '_name', attribute)
                    loader.add_value(field_name_part + '_visible', 1)
                    loader.add_value(field_name_part + '_global', 1)
                    if attribute == 'colors':
                        # Get the list of color names first
                        all_color_ids = dict(parent_details['attributes']['colors']['colorMap']).keys()
                        all_colors = []
                        for color in all_color_ids:
                            all_colors.append(parent_details['attributes']['colors']['colorMap'][color]['name'])

                        loader.add_value(field_name_part + '_values', ','.join(all_colors))
                        selected_color = str(parent_details['attributes']['colors']['selectedColor'])
                        loader.add_value(field_name_part + '_default', parent_details['attributes']['colors']['colorMap'][selected_color]['name'])
                    elif attribute == 'sizes':
                        # Get the list of size names first
                        all_size_ids = dict(parent_details['attributes']['sizes']['sizeMap']).keys()
                        all_sizes = []
                        for size in all_size_ids:
                            all_sizes.append(parent_details['attributes']['sizes']['sizeMap'][size]['name'])

                        loader.add_value(field_name_part + '_values', ','.join(all_sizes))
                        loader.add_value(field_name_part + '_default', '')
        else:
            loader.add_value('parent_sku', parent_details['sku'])
            loader.add_value('wp_product_type', 'variation')

            # Fill up the attributes
            if 'attributes' in parent_details:
                for index, attribute in enumerate(variation_attributes):
                    field_name_part = 'attribute' + str(index+1)
                    loader.add_value(field_name_part + '_name', attribute)
                    loader.add_value(field_name_part + '_visible', 1)
                    loader.add_value(field_name_part + '_global', 1)
                    if attribute == 'colors':
                        selected_color = str(sku_obj['traits']['colors']['selectedColor'])
                        loader.add_value(field_name_part + '_values', parent_details['attributes']['colors']['colorMap'][selected_color]['name'])

                        # The images for the variations are listed in color attribute
                        for image in parent_details['attributes']['colors']['colorMap'][selected_color]['imagery']['images']:
                            picture_urls.append(base_image_url + str(image['filePath']) + '?op_sharpen=1&wid=1230&hei=1500')
                    elif attribute == 'sizes':
                        selected_size = str(sku_obj['traits']['sizes']['selectedSize'])
                        loader.add_value(field_name_part + '_values', parent_details['attributes']['sizes']['sizeMap'][selected_size]['name'])


        loader.add_value('store', parent_details['store'])
        loader.add_value('name', parent_details['name'])
        loader.add_value('brand', parent_details['brand'])
        loader.add_value('tax_status', parent_details['tax_status'])
        loader.add_value('in_stock', 1 if sku_obj['availability']['available'] else 0)
        loader.add_value('backorders_allowed', parent_details['backorders_allowed'])
        loader.add_value('wp_published', parent_details['wp_published'])
        loader.add_value('wp_featured', parent_details['wp_featured'])
        loader.add_value('wp_visibility', parent_details['wp_visibility'])

        original_price_in_usd = parent_details['original_price_in_usd']

        category, weight, profit_margin_rate, estimated_shipping_cost_in_usd, estimated_profit_in_usd, final_price_in_usd, final_price_in_npr = self.map_and_calculate(store='Macys', category_list=category_list, original_price_in_usd=original_price_in_usd)
        loader.add_value('category', category)
        loader.add_value('weight', weight)
        loader.add_value('profit_margin_rate', profit_margin_rate)
        loader.add_value('original_price_in_usd', original_price_in_usd)
        loader.add_value('estimated_shipping_cost_in_usd', estimated_shipping_cost_in_usd)
        loader.add_value('estimated_profit_in_usd', estimated_profit_in_usd)
        loader.add_value('final_price_in_usd', final_price_in_usd)
        loader.add_value('final_price_in_npr', final_price_in_npr)
            
        loader.add_value('picture_urls', ','.join(picture_urls))

        loader.load_item()
        return loader


    def parse_sephora(self, product_url, html_dump):
        loaders = []

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
                shared_product_details['attributes'][product['variationType']] = [(obj.get('variationValue', '') + ' ' + obj.get('variationDesc', '')) for obj in product['regularChildSkus'] if obj['variationType'] == product['variationType']]

            sephora_category_list = self.recursive_sephora_category_builder(product['parentCategory'])
            
            if 'regularChildSkus' in product:
                is_variable_product = True
            else:
                is_variable_product = False

            loaders.append(self.gather_sephora_variation(sku_obj=product['currentSku'], parent_details=shared_product_details, category_list=sephora_category_list, is_parent=True, is_variable=is_variable_product))

            if is_variable_product:
                for child_sku_obj in product['regularChildSkus']:
                    loaders.append(self.gather_sephora_variation(sku_obj=child_sku_obj, parent_details=shared_product_details, category_list=sephora_category_list, is_parent=False, is_variable=True))

        return loaders

    def gather_sephora_variation(self, sku_obj, parent_details, category_list, is_parent, is_variable):
        loader = ProductItemLoader(item=Product(), selector=sku_obj)

        loader.add_value('product_url', parent_details['product_url'])
        if is_parent:
            loader.add_value('sku', parent_details['sku'])
            loader.add_value('wp_product_type', 'variable' if is_variable else 'simple')
            loader.add_value('description', parent_details['description'])
            loader.add_value('short_description', parent_details['short_description'])

            # Get all the keys of the attributes if it exists and fill the attribute details for parent (which includes all possible values)
            if 'attributes' in parent_details:
                variation_attributes = list(parent_details['attributes'].keys())

                for index, attribute in enumerate(variation_attributes):
                    field_name_part = 'attribute' + str(index+1)
                    loader.add_value(field_name_part + '_name', attribute)
                    loader.add_value(field_name_part + '_values', ','.join(parent_details['attributes'][attribute]))
                    loader.add_value(field_name_part + '_visible', 1)
                    loader.add_value(field_name_part + '_global', 1)
                    if attribute == sku_obj['variationType']:
                        loader.add_value(field_name_part + '_default', sku_obj.get('variationValue', '') + ' ' + sku_obj.get('variationDesc', ''))
        else:
            loader.add_value('parent_sku', parent_details['sku'])
            loader.add_value('wp_product_type', 'variation')

            # Fill up the attributes
            if 'attributes' in parent_details:
                variation_attributes = list(parent_details['attributes'].keys())

                for index, attribute in enumerate(variation_attributes):
                    field_name_part = 'attribute' + str(index+1)
                    loader.add_value(field_name_part + '_name', attribute)
                    loader.add_value(field_name_part + '_values', sku_obj.get('variationValue', '') + ' ' + sku_obj.get('variationDesc', ''))
                    loader.add_value(field_name_part + '_visible', 1)
                    loader.add_value(field_name_part + '_global', 1)


        loader.add_value('store', parent_details['store'])
        loader.add_value('name', parent_details['name'])
        loader.add_value('brand', parent_details['brand'])
        loader.add_value('tax_status', parent_details['tax_status'])
        loader.add_value('in_stock', 0 if sku_obj['isOutOfStock'] else 1)
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
            self.f_category_mapping_errors.write('"{0}"'.format(store) + "," + ",".join('"{0}"'.format(item) for item in padded_category_list) + "\n")
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
            self.f_profit_mapping_errors.write(",".join('"{0}"'.format(item) for item in qarece_category_list) + "\n")
            raise Exception("Could not find qarece category mapping in profit margin file for hierarchy of %s" % (qarece_category_list))
        
        # There should be only one match, if multiple, then there is an error within the file
        # Calculate final values to return
        item_weight = float(bizrules_match_df['avg_weight'])
        item_profit_margin_rate = .30
        item_estimated_shipping_cost_in_usd = max(item_weight * 5, 5)
        item_estimated_profit_in_usd = original_price_in_usd * item_profit_margin_rate
        item_final_price_in_usd = original_price_in_usd + item_estimated_shipping_cost_in_usd + item_estimated_profit_in_usd
        item_final_price_in_npr = self.usd_to_npr(item_final_price_in_usd)
        item_category_hierarchy = '>'.join(list(filter(None, qarece_category_list))) # Keep only values that are not empty

        return item_category_hierarchy, item_weight, item_profit_margin_rate, item_estimated_shipping_cost_in_usd, item_estimated_profit_in_usd, item_final_price_in_usd, item_final_price_in_npr

    def usd_to_npr(self, usd_price):
        return roundup_to_hundred(float(usd_price) * 112)

