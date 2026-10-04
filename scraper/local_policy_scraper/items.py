import scrapy

class SchemeItem(scrapy.Item):
    name = scrapy.Field()
    launching_authority = scrapy.Field()
    category = scrapy.Field()
    launch_date = scrapy.Field()
    target_beneficiaries = scrapy.Field()
    budget_allocated = scrapy.Field()
    description = scrapy.Field()
    source_url = scrapy.Field()

class MentionItem(scrapy.Item):
    scheme_name = scrapy.Field() # Used for lookup
    source = scrapy.Field()
    raw_text = scrapy.Field()
    language = scrapy.Field()
    published_date = scrapy.Field()
    url = scrapy.Field()
