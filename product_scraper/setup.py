import os

if os.path.exists("./product_scraper/output/category_mapping_errors.csv"):
    os.remove("./product_scraper/output/category_mapping_errors.csv")

if os.path.exists("./product_scraper/output/profit_mapping_errors.csv"):
    os.remove("./product_scraper/output/profit_mapping_errors.csv")

if os.path.exists("./product_scraper/output/errors.txt"):
    os.remove("./product_scraper/output/errors.txt")

if os.path.exists("./product_scraper/output/products_to_unpublish.csv"):
    os.remove("./product_scraper/output/products_to_unpublish.csv")

# Fill in the headers for products to unpublish file
f_products_to_unpublish = open(os.path.dirname(__file__) + "product_scraper/output/products_to_unpublish.csv", "a")
f_products_to_unpublish.write('SKU,Published' + "\n")
f_products_to_unpublish.close()