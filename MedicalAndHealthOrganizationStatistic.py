#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig

class ScrapyConfig(ScrapyWrapperConfig):
	def url_generator(self):
		prefix = "http://www.nhfpc.gov.cn/mohwsbwstjxxzx/s8208/list"
		suffix = ".shtml"
		yield prefix + suffix
		for i in range(2, 15):
			yield prefix + "_" + str(i) + suffix

	begin_urls = url_generator

	steps = {
		"begin": {
			'res': {
				'selector_xpath': '//div[@class = "contents"]//a/@href',
				'next_step': 'content'
			}
		},
		"content": {
			'res': {
				'selector_css': '#page_content',
				'next_step': 'db'
			}
		},
		"db": {
			'type': "db",
			'table_name': "MedicalAndHealthOrganizationStatistic",
			'fields': [{
				'name': "PublicationDate",
				'selector_css': 'div.content_subtitle',
				'selector_regex': u'([0-9]{4}-[0-9]{2}-[0-9]{2})',
				'required': True
			}, {
				'name': "Headline",
				'selector_css': '#zoomtitle',
				'required': True
			}, {
				'name': "DetailContent",
				'selector_css': '#zoomcon',
				'strip_tags': False,
				'required': True
			}
			]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

