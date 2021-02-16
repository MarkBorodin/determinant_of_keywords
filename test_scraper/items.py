# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Home_Page(scrapy.Item):
    uuid = scrapy.Field()
    url = scrapy.Field()
    sitemap_exists = scrapy.Field()


class Subpage(scrapy.Item):
    uuid = scrapy.Field()
    url = scrapy.Field()
    indexed_in_sitemap = scrapy.Field()
    robots_follow_no_follow = scrapy.Field()
    home_page = scrapy.Field()
    subpage = scrapy.Field()
    site_title = scrapy.Field()
    meta_description = scrapy.Field()
    appearance_position = scrapy.Field()
    text = scrapy.Field()
