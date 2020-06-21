# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

import json
import logging
import random
import datetime
from urllib.parse import urlparse
from html.parser import HTMLParser
from scrapy import signals
from scrapy.conf import settings
from selenium import webdriver
from scrapy.http import HtmlResponse
from selenium.webdriver import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

logger = logging.getLogger(__name__)


class RandomUserAgentMiddleware(object):
	def process_request(self, request, spider):
		ua = random.choice(settings.get('USER_AGENT_LIST'))
		if ua:
			request.headers.setdefault('User-Agent', ua)


class ProxyMiddleware(object):
	def process_request(self, request, spider):
		proxy = random.choice(settings.get('PROXIES'))
		request.meta['proxy'] = "{0}".format(proxy['ip_port'])


class ScannerSpiderMiddleware(object):
	def __init__(self):
		proxy = random.choice(settings.get('PROXIES'))
		d = DesiredCapabilities.CHROME
		d['loggingPrefs'] = {'performance': 'INFO'}  # ALL/INFO
		chrome_options = webdriver.ChromeOptions()
		chrome_options.add_argument('--headless')
		chrome_options.add_argument('--disable-gpu')
		chrome_options.add_argument('--ignore-certificate-errors')
		chrome_options.add_argument('blink-settings=imagesEnabled=false')
		chrome_options.add_argument('--proxy-server=http://{0}'.format(proxy['ip_port']))
		chrome_options.add_argument(
			'--user-agent= Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36')
		chrome_options.add_experimental_option("prefs", {'download.default_directory': "/tmp/",
														 "download.prompt_for_download": True})
		self.driver = webdriver.Chrome(chrome_options=chrome_options, desired_capabilities=d)

	@classmethod
	def from_crawler(cls, crawler):
		s = cls()
		crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
		return s

	def process_request(self, request, spider):
		request.meta['start_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		self.driver.get(request.url)
		return HtmlResponse(url=self.driver.current_url, body=self.driver.page_source, request=request,
							encoding="utf-8")

	def process_response(self, request, response, spider):
		request.meta['finish_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		headers = self.driver.get_log('performance')
		for header in headers:
			try:
				_response = json.loads(header[u'message'])[u'message'][u'params'][u'response']
				if _response[u'url'] == self.driver.current_url:
					response.headers = _response[u'headers']
					response.status = _response[u'status']
					response.reason = _response[u'statusText']
					response.protocol = _response[u'protocol']
					break
			except:
				pass
		urlsplit = urlparse(response.request.url)
		paths = urlsplit.path.split('.')
		if len(paths) == 2:
			extension = paths[-1]
			if extension in ['swf', 'gif', 'jpg', 'pdf', 'mp4', 'jpeg']:
				return response
		if 'Content-Type' in response.headers:
			content_type = response.headers['Content-Type']
			if content_type in settings.get('STATIC_FILES'):
				return response
		js = """
						window.alert = function(){return false;};
						window.prompt = function(msg,input){return input;};
						window.confirm = function(){return true;};
						window.close = function(){return false;};
					"""
		self.driver.execute_script(js)
		submits = self.driver.find_elements_by_xpath('//*[@type="submit"]')
		if len(submits) > 0:
			for i in range(0, len(submits)):
				submits = self.driver.find_elements_by_xpath('//*[@type="submit"]')
				try:
					submit = submits[i]
					ActionChains(self.driver).click(submit).perform()
				except:
					pass

		onclicks = self.driver.find_elements_by_xpath('//*[@onClick]')
		if len(onclicks) > 0:
			for i in range(0, len(onclicks)):
				onclicks = self.driver.find_elements_by_xpath('//*[@onClick]')
				try:
					onclick = onclicks[i]
					ActionChains(self.driver).click(onclick).perform()
				except:
					pass

		return response

	def spider_closed(self, spider, reason):
		self.driver.quit()
