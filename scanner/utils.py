#!/usr/bin/env python
# encoding: utf-8

"""
@author: xl7dev
@contact: root@safebuff.com
@time: 2017/6/12 上午10:12
"""
import re
import urllib
import requests
from lxml import etree


def baidu_search(query):
	base_url = 'http://www.baidu.com/s'
	full_query = 'site:' + query + " -html"
	urls = []
	page = 0
	nr = 50
	new = True
	headers = {
		"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36"}
	for page in range(1, 5):
		url = '%s?pn=%d&rn=50&wd=%s' % (base_url, page * nr, urllib.quote_plus(full_query))
		try:
			resp = requests.get(url, headers=headers, timeout=30)
			if resp.status_code != 200:
				break
		except requests.ConnectionError as e:
			print e
			break
		html = etree.HTML(resp.text)
		hrefs = html.xpath('//a[@class="c-showurl"]/@href')
		for href in hrefs:
			resp = requests.get(href)
			urls.append(resp.url)
	return list(set(urls))
