import os

if os.path.exists("./product_scraper/output/category_mapping_errors.csv"):
    os.remove("./product_scraper/output/category_mapping_errors.csv")

if os.path.exists("./product_scraper/output/profit_mapping_errors.csv"):
    os.remove("./product_scraper/output/profit_mapping_errors.csv")

if os.path.exists("./product_scraper/output/errors.txt"):
    os.remove("./product_scraper/output/errors.txt")