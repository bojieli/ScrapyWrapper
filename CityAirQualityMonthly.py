#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig

class ScrapyConfig(ScrapyWrapperConfig):
	def url_gen(self):
		for i in range(0,5):
			yield "http://www.zhb.gov.cn/hjzl/dqhj/cskqzlzkyb/index" + ("_" + str(i) if i > 0 else "") + ".shtml"

	begin_urls = url_gen

	steps = {
		"begin": {
			'res': {
				'selector_css': '.main_rt_list li',
				'next_step': 'list'
			}
		},
		"list": {
			'type': 'intermediate',
			'fields': [{
				'name': "PublicationDate",
				'selector_css': 'span',
				'data_type': "Date",
				'required': True
			}, {
				'name': "Headline",
				'selector_xpath': '//a/@title',
				'required': True
			}],
			'res': [{
				'selector_xpath': '//a/@href',
				'selector_regex': '(\./.*\.shtml)',
				'next_step': 'content'
			}, {
				'selector_xpath': '//a/@href',
				'selector_regex': '(\./.*\.pdf)',
				'next_step': 'pdf'
			}]
		},
		"content": {
			'res': {
				'selector_css': 'div.main',
				'next_step': 'db'
			}
		},
		"db": {
			'type': "db",
			'table_name': "CityAirQualityMonthly",
			'fields': [{
				'name': 'DetailContent',
				'selector_css': '.wzxq_neirong2',
				'strip_tags': False,
				'download_images': True,
				'required': True
			}]
		},
		"pdf": {
			'type': "file",
			'res': {
				'next_step': 'db_pdf'
			}
		},
		'db_pdf': {
			'type': 'db',
			'table_name': "CityAirQualityMonthly",
			'fields': [{
				'name': 'DetailContent',
				'selector': lambda _, meta: meta['$$filepath'],
				'required': True
			}]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

