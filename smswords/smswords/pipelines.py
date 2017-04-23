# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import MySQLdb

from scrapy.conf import settings


class SmswordsPipeline(object):
        
    def process_item(self, item, spider):
        """
        :type item: mobile_numbers item
        """
        ## DB Connection
        conn = MySQLdb.connect(host=settings["HOST"], user=settings["USER"], \
                    passwd=settings["PASSWD"], db=settings["DATABASE"], charset="utf8", \
                        use_unicode=True)
        cursor = conn.cursor()

        query = "INSERT INTO mobile_numbers (`number`, `country_code`, city_id, area_id, \
            district_id, postal_code_id, created_at, updated_at) VALUES (%s, %s, %s, \
                %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE updated_at = %s"
        values = (item["number"], item["country_code"], item["city_id"], \
                item["area_id"], item["district_id"], item["postal_code_id"], \
                    item["created_at"], item["updated_at"], item["updated_at"])

        cursor.execute(query, values)
        conn.commit()

        conn.close()

        return item
