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
				'selector': lambda s: s.split(',')[1],
				'next_step': 'list'
			},
			'fields': [{
				'name': 'StockCode',
				'skip': True
			}]
		},
		"list": {
			'req': {
				'url': lambda url, meta: 'http://data.eastmoney.com/notices/stock/' + str(url) + '.html'
			},
			'res': {
				'selector_css': '#dt_1 td a::href',
				'next_step': 'content'
			},
			'fields': [{
				'name': 'CompanyID',
				'reference': {
					'table': 'PublicCompanyInfo',
					'field': 'StockCode',
					'remote_field': 'StockCode'
				},
				'required': True
			}, {
				'name': 'ReportDate',
				'data_type': 'Date'
			}, {
				'name': 'StockCode',
				'selector': lambda result, meta: meta['StockCode']
			}]
		},
		"content": {
			'res': {
				'selector_css': '',
				'next_step': 'db'
			},
			'fields': [
			]
		},
		"db": {
			'type': "db",
			'table_name': "PublicCompanyReport"
		}
	}

class Spider(SpiderWrapper):
	name = 'PublicCompanyInfo'
	config = ScrapyConfig()

