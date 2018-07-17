# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ScannerItem(scrapy.Item):
	url = scrapy.Field()
	method = scrapy.Field()
	headers = scrapy.Field()
	scheme = scrapy.Field()
	port = scrapy.Field()
	path = scrapy.Field()
	extension = scrapy.Field()
	reason = scrapy.Field()
	http_version = scrapy.Field()
	raw = scrapy.Field()
	start_time = scrapy.Field()
	finish_time = scrapy.Field()
	status_code = scrapy.Field()
	response_headers = scrapy.Field()
	content = scrapy.Field()