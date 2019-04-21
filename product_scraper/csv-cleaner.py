import pandas as pd

products_df = pd.read_csv('./product_scraper/output/Product.csv', index_col=False)

# print(products_df.info())

products_df = products_df[[
    'wp_product_type', 
    'product_url',
    'product_id',
    'sku', 
    'parent_sku',
    'name', 
    'brand',
    'store',
    'wp_published', 
    'wp_featured', 
    'wp_visibility', 
    'short_description', 
    'description', 
    'tax_status',
    'in_stock',
    'backorders_allowed',
    'weight',
    'profit_margin_rate',
    'original_price_in_usd',
    'estimated_shipping_cost_in_usd',
    'estimated_profit_in_usd',
    'final_price_in_usd',
    'final_price_in_npr',
    'category',
    'picture_urls',
    'swatch_url',
    'attribute1_name',
    'attribute1_values',
    'attribute1_visible',
    'attribute1_global',
    'attribute1_default',
    'attribute2_name',
    'attribute2_values',
    'attribute2_visible',
    'attribute2_global',
    'attribute2_default',
    'attribute3_name',
    'attribute3_values',
    'attribute3_visible',
    'attribute3_global',
    'attribute3_default'
    ]]

products_df = products_df.rename(columns={
    'product_url': 'Meta: Product url',
    'product_id': 'Product id', 
    'sku': 'SKU',
    'parent_sku': 'Parent',
    'store': 'Meta: Store',
    'name': 'Name',
    'brand': 'Brand',
    'description': 'Description',
    'short_description': 'Short description',
    'category': 'Categories',
    'weight': 'Meta: Weight',
    'profit_margin_rate': 'Meta: Profit margin rate',
    'original_price_in_usd': 'Meta: Original price in usd',
    'estimated_shipping_cost_in_usd': 'Meta: Estimated shipping cost in usd',
    'estimated_profit_in_usd': 'Meta: Estimated profit in usd',
    'final_price_in_usd': 'Meta: Final price in usd',
    'final_price_in_npr': 'Regular price',
    'picture_urls': 'Images',
    'swatch_url': 'Swatch url',
    'tax_status': 'Tax status',
    'in_stock': 'In stock?',
    'backorders_allowed': 'Backorders allowed?',
    'attribute1_name': 'Attribute 1 name',
    'attribute1_values': 'Attribute 1 value(s)',
    'attribute1_visible': 'Attribute 1 visible',
    'attribute1_global': 'Attribute 1 global',
    'attribute1_default': 'Attribute 1 default',
    'attribute2_name': 'Attribute 2 name',
    'attribute2_values': 'Attribute 2 value(s)',
    'attribute2_visible': 'Attribute 2 visible',
    'attribute2_global': 'Attribute 2 global',
    'attribute2_default': 'Attribute 2 default',
    'attribute3_name': 'Attribute 3 name',
    'attribute3_values': 'Attribute 3 value(s)',
    'attribute3_visible': 'Attribute 3 visible',
    'attribute3_global': 'Attribute 3 global',
    'attribute3_default': 'Attribute 3 default',
    'wp_product_type': 'Type',
    'wp_published': 'Published',
    'wp_featured': 'Is featured?',
    'wp_visibility': 'Visibility in catalog'
})

print(products_df.info())

products_df.to_csv('./product_scraper/output/Product-formatted-for-wp.csv', index=False)

## Reformatting error file
try:
    category_mapping_errors_df = pd.read_csv('./product_scraper/output/category_mapping_errors.csv', header=None, index_col=False)
    category_mapping_errors_df.drop_duplicates(keep='first', inplace=True)
    category_mapping_errors_df.to_csv('./product_scraper/output/category_mapping_errors.csv', header=False, index=False)
except:
    print("We got some errors while reformatting category mapping error file")

try:
    profit_mapping_errors_df = pd.read_csv('./product_scraper/output/profit_mapping_errors.csv', header=None, index_col=False)
    profit_mapping_errors_df.drop_duplicates(keep='first', inplace=True)
    profit_mapping_errors_df.to_csv('./product_scraper/output/profit_mapping_errors.csv', header=False, index=False)
except:
    print("We got some errors while reformatting profit mapping error file")
