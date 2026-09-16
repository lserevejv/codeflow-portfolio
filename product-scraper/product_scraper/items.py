import scrapy


class ProductItem(scrapy.Item):
    product_id = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    description = scrapy.Field()
    availability = scrapy.Field()
    url = scrapy.Field()
    images = scrapy.Field()
    category = scrapy.Field()
    brand = scrapy.Field()
    scraped_at = scrapy.Field()
    source_domain = scrapy.Field()