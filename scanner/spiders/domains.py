# -*- coding: utf-8 -*-
import scrapy
import os
import re
import json
import requests
from urllib.parse import urlparse
from scanner.items import ScannerItem
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

"""
	> redis-server
	> scrapy crawl domains -a domain=testphp.vulnweb.com
"""


def process_value(value):
	"""
	接收从标签提取的每个值和扫描的属性并且可以修改值并返回新值的函数，或者返回 None 以完全忽略链接。如果没有给出，process_value 默认为 lambda x: x
	:param value:
	:return:
	"""
	try:
		window = re.search("window.open\([\'|\"](.*?)[\'|\"]", value, flags=re.I)
		location = re.search("location.href=[\'|\"](.*?)[\'|\"]", value, flags=re.I)
		javascript = re.search("[\'|\"](.*?)[\'|\"]", value, flags=re.I)
		if window:
			return window.group(1)
		elif location:
			return location.group(1)
		elif javascript:
			return javascript.group(1)
		else:
			return value
	except Exception as e:
		print(value, e)
		return value


class DomainsSpider(CrawlSpider):
	name = "domains"
	IGNORED_EXTENSIONS = []

	rules = (
		Rule(LinkExtractor(deny_extensions=IGNORED_EXTENSIONS, allow=('.*'),
						   tags=(
							   "a", "area", "link", "img", "form", "embed", "iframe", "source", "script", "item",
							   "meta"),
						   attrs=('href', 'src', 'action', 'url', 'name', 'onclick',), process_value=process_value),
			 callback='parse_item', follow=True),
	)

	def __init__(self, domain='', cookies='', filename='', *args, **kwargs):
		super(DomainsSpider, self).__init__(*args, **kwargs)
		allowed_domain = domain if not domain.startswith('http://') or domain.startswith('https://') else urlparse(
			domain).netloc
		self.allowed_domains = [allowed_domain]
		domain = domain if domain.startswith('http://') or domain.startswith('https://') else 'http://' + domain
		self.start_urls = [domain]
		self.cookies = cookies
		self.filenames = [x.strip() for x in open(os.path.abspath(filename))] if filename else ''
		self.again = 1

	def parse_item(self, response):
		item = ScannerItem()
		url = response.url
		# fuzz url
		if self.again == 1:
			if '?' in url:
				base_url = '/'.join(url.split('?')[0].split('/')[:-1])
			else:
				base_url = '/'.join(url.split('/')[:-1])
			fuzz_urls = list(map(lambda x: (base_url + x) if x.startswith('/') else base_url + "/" + x, self.filenames))
			self.again = 2
			for url in fuzz_urls:
				yield scrapy.Request(url, callback=self.parse_fuzz)
		_headers = response.request.headers
		headers = {}
		for x in _headers:
			headers[x.decode()] = _headers[x].decode()
		urlsplit = urlparse(response.request.url)
		netlocs = urlsplit.netloc.split(':')
		if len(netlocs) == 2:
			port = int(netlocs[-1])
		else:
			port = 80
		paths = urlsplit.path.split('.')
		if len(paths) == 2:
			extension = paths[-1]
		else:
			extension = ''
		raw = ''
		if extension in ['gif', 'jpg', 'swf', 'pdf']:
			content = ''
		else:
			content = response.text
		status_code = response.status
		item['url'] = url
		item['method'] = response.request.method
		item['headers'] = headers
		item['scheme'] = urlsplit.scheme
		item['port'] = port
		item['path'] = urlsplit.path
		item['extension'] = extension
		item['reason'] = response.reason
		item['http_version'] = response.protocol
		item['raw'] = raw
		item['start_time'] = response.request.meta['start_time']
		item['finish_time'] = response.request.meta['finish_time']
		item['status_code'] = status_code
		item['response_headers'] = response.headers
		item['content'] = content
		yield item

	def parse_fuzz(self, response):
		item = ScannerItem()
		url = response.url
		_headers = response.request.headers
		headers = {}
		for x in _headers:
			headers[x.decode()] = _headers[x].decode()
		urlsplit = urlparse(response.request.url)
		netlocs = urlsplit.netloc.split(':')
		if len(netlocs) == 2:
			port = int(netlocs[-1])
		else:
			port = 80
		paths = urlsplit.path.split('.')
		if len(paths) == 2:
			extension = paths[-1]
		else:
			extension = ''
		raw = ''
		if extension in ['gif', 'jpg', 'swf', 'pdf']:
			content = ''
		else:
			content = response.text
		status_code = response.status
		item['url'] = url
		item['method'] = response.request.method
		item['headers'] = headers
		item['scheme'] = urlsplit.scheme
		item['port'] = port
		item['path'] = urlsplit.path
		item['extension'] = extension
		item['reason'] = response.reason
		item['http_version'] = response.protocol
		item['raw'] = raw
		item['start_time'] = response.request.meta['start_time']
		item['finish_time'] = response.request.meta['finish_time']
		item['status_code'] = status_code
		item['response_headers'] = response.headers
		item['content'] = content
		yield item

	def _requests_to_follow(self, response):
		"""
			重写Rule函数
		"""
		seen = set()
		for n, rule in enumerate(self._rules):
			links = [lnk for lnk in rule.link_extractor.extract_links(response) if lnk not in seen]
			if links and rule.process_links:
				links = rule.process_links(links)
			for link in links:
				seen.add(link)
				r = self._build_request(n, link)
				yield rule.process_request(r, response)
