# Qarece Web Crawler

## Author: Vivek Pandey

## Save hours spent on manually adding and updating products to your e-commerce site and do it in seconds!

### This web crawler gathers the latest details, variations, imagery and pricing informations of a catalog of products given their urls from their corresponding online stores and prepares files ready for upload to your e-commerce platfrom. It was built with the purposes of making product additions easier for e-commerce retailers.

## Supported Ecommerce Stores

- Macys
- Sephora
- 6pm (Future Enchancement)
- Amazon (Future Enhancement)

## Output Files Customized for Platforms

- Woocommerce (De-Facto)

## Important Notes

- The internal category mapping, profit rates, and shipping rates are to be adjusted by you according to your business logic in the reference files located at `product_scraper/product_scraper/reference_data` folder. The current values are default placeholders.

## Custom Enhancements for Your Business

This crawler prototype was initially built as per the needs of Qarece - New York. If you want a custom implementation or enhancement for your e-commerce business, reach out to the author at `viveckh@hotmail.com`.

Development rates are on a hourly basis or project basis depending on your needs.

## How to Run

- Clone the Repo (Duh)
- Make sure you have Python, Scrapy and Pandas installed in your system
- Add the urls of products you want to crawl by going to `/product_scraper/product_scraper/input/urls.txt`. Check the supported e-commerce stores above.
- Navigate back to the base of the scraper where the scrapy.cfg file is. `cd /product_scraper`
- `python setup.py`
- `scrapy crawl products-spider`
- `python clean-scraped-results.py`
- The output file to upload in woocommerce is ready at `/product_scraper/product_scraper/output/Product-formatted-for-wp.csv`. Run it twice, once in a new products import mode, and again in update mode to update existing products
- The output file to hide products that are no longer available in market will be ready at `/product_scraper/product_scraper/output/products_to_unpublish.csv`. Run it once in update mode to hide products that exist in your catalog but are not available in the market anymore.
- Any products that could not be crawled successfully with associated errors will be detailed in `/product_scraper/product_scraper/output/errors.txt`

## TODO
- An automated way to update catalog in woocommerce using output files without having to upload manually
- An automated script to prepare `urls.txt` by exporting the catalog from woocommerce in csv, and making a list of product's market urls