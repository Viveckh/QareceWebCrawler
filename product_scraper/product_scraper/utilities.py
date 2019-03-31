from scrapy.loader.processors import TakeFirst, Compose, MapCompose, Join
import math

clean_text = Compose(MapCompose(lambda v: v.strip()), Join())   
to_int = Compose(TakeFirst(), int)
to_float = Compose(TakeFirst(), float)

def extract_with_css(response, query):
    return response.css(query).get(default='').strip()

def roundup_to_hundred(x):
    return int(math.ceil(x / 100.0)) * 100