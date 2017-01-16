#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig

class ScrapyConfig(ScrapyWrapperConfig):
	def url_generator(self):
		for i in range(1,15000):
			#yield 'http://db.yaozh.com/api/index.php/Home/index/yaopinjiage/id/' + str(i)
			yield 'http://db.yaozh.com/jp/' + str(i) + '.html'

	crawlera_enabled = True

	begin_urls = url_generator

	steps = {
		"begin": {
			'fields': [{'name': '$$id', 'selector_regex': '([0-9]*).html', 'required': True}],
			'res': [{
				'selector_css': 'tr.d',
				'next_step': 'detail-fields'
			}, {
				'selector_regex': u'(您的操作过于频繁，请验证后继续使用)',
				'selector': lambda _, meta: meta['$$url'],
				'next_step': 'begin'
			}]
		},
		"detail-fields": {
			'type': 'intermediate',
			'fields': [{
				'name': "DrugMarketDate",
				'selector_xpath': "//td[3]",
				'data_type': 'Date'
			}],
			'res': {
				'selector_xpath': '//td[1]',
				'strip_tags': True,
				'data_postprocessor': lambda name, meta: 'http://db.yaozh.com/jp?name=&jan=&tname=' + name + '&jc_be_jp.me_tname=1&bname=&company=&date=',
				'next_step': 'search'
			}
		},
		"search": {
			'req': {
				'dont_filter': True
			},
			'res': [{
				'selector_css': 'table.table-striped tr',
				'data_validator': lambda text, meta: '/jp/' + meta['$$id'] + '.html' in text,
				'next_step': 'db'
			}, {
				'selector_regex': u'(您的操作过于频繁，请验证后继续使用)',
				'selector': lambda _, meta: meta['$$url'],
				'next_step': 'search'
			}]
		},
		"db": {
			'type': "db",
			'table_name': "JapanMedicalProductInfo",
			'unique': ['JapaneseGenericName', 'JapaneseRetailName', 'CompanyName'],
			'upsert': True,
			'fields': [{
				'name': 'JapaneseGenericName',
				'selector_xpath': '//td[1]',
				'required': True
			}, {
				'name': 'JapaneseRetailName',
				'selector_xpath': '//th',
				'required': True
			}, {
				'name': 'EnglishGenericName',
				'selector_xpath': '//td[2]'
			}, {
				'name': 'CompanyName',
				'selector_xpath': '//td[3]'
			}, {
				'name': 'DrugManual',
				'selector_xpath': '//td[5]/a/@href'
			}]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

