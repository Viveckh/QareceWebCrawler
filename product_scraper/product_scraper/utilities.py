from scrapy.loader.processors import TakeFirst, Compose, MapCompose, Join

clean_text = Compose(MapCompose(lambda v: v.strip()), Join())   
to_int = Compose(TakeFirst(), int)

def extract_with_css(response, query):
    return response.css(query).get(default='').strip()