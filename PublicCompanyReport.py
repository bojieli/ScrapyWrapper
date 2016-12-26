#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderWrapper
from scrapywrapper.config import ScrapyWrapperConfig

class ScrapyConfig(ScrapyWrapperConfig):
	begin_urls = ["http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=C.BK04651&sty=FCOIATA&sortType=C&sortRule=-1&page=1&pageSize=1000&js=var%20quote_123%3d{rank:[(x)],pages:(pc)}&token=7bc05d0d4c3c22ef9fca8c2a912d779c&jsName=quote_123&_g=0.0603660640467345"]
	steps = {
		"begin": {
			'res': {
			    'parser': 'js-string',
				'selector': lambda s, meta: s.split(',')[1],
				'next_step': 'list'
			}
		},
		"list": {
			'req': {
				'url': lambda url, meta: 'http://data.eastmoney.com/notices/stock/' + str(url) + '.html',
				'webview': True
			},
			'res': {
				'selector_css': '#dt_1 tr',
				'next_step': 'list_parse'
			},
			'fields': [{
				'name': '$$StockCode'
			}]
		},
		"list_parse": {
			'type': 'intermediate',
			'res': {
				'selector_xpath': '//a/@href',
				'next_step': 'content'
			},
			'fields': [{
				'name': 'ReportType',
				'selector_xpath': '//td[2]'
			}, {
				'name': 'ReportDate',
				'selector_xpath': '//td[3]',
				'data_type': 'Date'
			}]
		},
		"content": {
			'res': {
				'selector_css': 'div.content',
				'next_step': 'db'
			},
		},
		"db": {
			'type': "db",
			'table_name': "PublicCompanyReport",
			'fields': [{
				'name': 'CompanyID',
				'reference': {
					'table': 'PublicCompanyInfo',
					'field': '$$StockCode',
					'remote_field': 'StockCode'
				},
				'required': True
			}, {
				'name': 'ReportNumber',
				'selector_xpath': 'div.detail-body',
				'selector_regex': u'公告编号：([0-9-]*)'
			}, {
				'name': 'Headline',
				'selector_css': 'div.detail-header h1'
			}, {
				'name': 'DetailContent',
				'selector_xpath': 'div.detail-body'
			}]
		}
	}

class Spider(SpiderWrapper):
	name = 'PublicCompanyInfo'
	config = ScrapyConfig()
