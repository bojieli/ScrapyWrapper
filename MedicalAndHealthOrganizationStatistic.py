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
				'selector_css': '.list',
				'next_step': 'db',
				'required': True
			}
		},
		"db": {
			'type': "db",
			'table_name': "MedicalAndHealthOrganizationStatistic",
			'fields': [{
				'name': "PublicationDate",
				'selector_css': 'div.source',
				'selector_regex': u'发布时间：\s*([0-9]{4}-[0-9]{2}-[0-9]{2})',
				'data_type': 'Date',
				'required': True
			}, {
				'name': "Headline",
				'selector_css': '.tit',
				'required': True
			}, {
				'name': "DetailContent",
				'selector_css': '#xw_box',
				'strip_tags': False,
				'download_images': True,
				'required': True
			}
			]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

