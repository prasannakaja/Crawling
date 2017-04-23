# -*- coding: utf-8 -*-
import random
import re

import scrapy
from scrapy.selector import Selector

from smswords.utils import *

def random_proxy(proxies):
    rproxy = random.choice(proxies)
    proxy = "http://%s" %rproxy.split('@')[-1]
    return proxy

def clean_text(text):
    text = text.replace('\n',' ').replace('\r', ' ').replace('\t', ' ')
    text = text.lstrip().rstrip().strip()
    return text

class MilanunciosSpider(scrapy.Spider):
    name = "milanuncios"
    allowed_domains = ["milanuncios.com"]
    start_urls = (
        'http://www.milanuncios.com/',
    )

    proxies = getProxies()
        
    def parse(self, response):
        self.categories_list_xpath = '//div[@class="cat2Item"]/a/@href'
        doc = Selector(response)
        listing_pages = doc.xpath(self.categories_list_xpath)
        
        for lpage in listing_pages[:3]:
            lpage = "http://www.milanuncios.com"+lpage.extract()
            request = scrapy.Request(lpage, callback=self.parse_listing)
            #request.meta['proxy'] = random_proxy(MilanunciosSpider.proxies)
            yield request


    def parse_listing(self, response):
        doc = Selector(response)
        ads = doc.xpath('//div[@class="aditem"]')
        for ad in ads:
            result_text =  ad.xpath('.//div[@class="aditem-header"]/div[2]//text()').extract()
            ## CITY
            city = result_text[0].split('(')[-1].strip(')').strip()

            ## AREA
            area = re.findall('.*\s+en\s+(.*?)\(.*', result_text[0])
            area = area[0].strip() if area else ""

            ## Phone NUmber
            phone_number = ad.xpath('.//div[@class="aditem-buttons"]//a/@href').extract()
            phone_number = phone_number[0].split(':od(')[-1].strip(');').strip() if phone_number else ""

            ## AD-Link
            rlink = ad.xpath('.//div[@class="aditem-detail"]/a/@href').extract()
            reference_link = "http://www.milanuncios.com"+rlink[0].strip() if rlink else ""

            ## AD-Title
            title = ad.xpath('.//div[@class="aditem-detail"]/a/text()').extract()
            ad_title = clean_text(title[0]) if title else ""

            #print "<>#<>".join([city, area, phone_number, reference_link, ad_title])
             

        
       
        
 
