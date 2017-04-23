# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Field

class MobileNumbersItem(scrapy.Item):
    # define the fields for your item here like:

    number = Field()
    country_code = Field()
    city_id = Field()
    area_id = Field()
    district_id = Field()
    postal_code_id = Field()
    deleted_at = Field()
    created_at = Field()
    updated_at = Field()

