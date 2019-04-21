# Qarece Automated E-commerce Catalog Management Web Crawler (AECMWC)
## Author: Vivek Pandey
## Save hours spent on manually adding and updating products to your e-commerce site and do it in seconds!

### This web crawler gathers the latest details, variations, imagery and pricing informations of a catalog of products given their urls from their corresponding online stores and prepares files ready for upload to your e-commerce platfrom. It was built with the purposes of making product additions easier for e-commerce retailers.


## Supported Ecommerce Stores
* Macys
* Sephora
* 6pm (Future Enchancement)
* Amazon (Future Enhancement)

## Output Files Customized for Platforms
* Woocommerce (De-Facto)

## Important Notes
* The internal category mapping, profit rates, and shipping rates are to be adjusted by you according to your business logic in the reference files located at `product_scraper/product_scraper/reference_data` folder. The current values are default placeholders.

## Custom Enhancements for Your Business
This crawler prototype was initially built as per the needs of Qarece - New York. If you want a custom implementation or enhancement for your e-commerce business, reach out to the author at `viveckh@hotmail.com`. 

Development rates are on a hourly basis or project basis depending on your needs.

## How to Run
* Clone the Repo (Duh)
* Make sure you have Python, Scrapy and Pandas installed in your system
* Add the urls of products you want to crawl by going to `/product_scraper/product_scraper/input/urls.txt`. Check the supported e-commerce stores above.
* Navigate back to the base of the scraper where the scrapy.cfg file is. `cd /product_scraper`
* `python setup.py`
* `scrapy crawl products-scraper`
* `python csv-cleaner.py`
* The output file to upload in woocommerce is ready at `/product_scraper/product_scraper/output/Product-formatted-for-wp.csv`
* Any products that could not be crawled successfully with associated errors will be detailed in `/product_scraper/product_scraper/output/errors.txt`