#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
import datetime

class ScrapyConfig(ScrapyWrapperConfig):
	begin_urls = ["http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=C.BK04651&sty=FCOIATA&sortType=C&sortRule=-1&page=1&pageSize=1000&js=var%20quote_123%3d{rank:[(x)],pages:(pc)}&token=7bc05d0d4c3c22ef9fca8c2a912d779c&jsName=quote_123&_g=0.0603660640467345"]
	steps = {
		"begin": {
			'res': {
			    'parser': 'js-object',
				'selector_json': 'rank',
				'selector': lambda s, meta: s.split(',')[1],
				'next_step': 'content'
			}
		},
		"content": {
			'req': {
				'url': lambda url, meta: 'http://f10.eastmoney.com/f10_v2/BusinessAnalysis.aspx?code=sz' + str(url) + '#zyfw-0'
			},
			'res': {
				'selector_css': 'div.section.first > div.article',
				'strip_tags': True,
				'next_step': 'db'
			},
			'fields': [{
				'name': '$$StockCode'
			}]
		},
		"db": {
			'type': "db",
			'table_name': "PublicCompanyCoreBusiness",
			'unique': ['CompanyID'],
			'upsert': True,
			'fields': [{
				'name': 'CompanyID',
				'reference': {
					'field': '$$StockCode',
					'table': 'PublicCompanyInfo',
					'remote_field': 'StockCode'
				},
				'required': True
			}, {
				'name': "ScopeOfBusiness",
				'required': True
			}, {
				'name': "ReportDate",
				'selector': lambda r, m: datetime.datetime.now().strftime('%Y-%m-%d')
			}
			]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

