#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
import datetime
from lxml.html import parse

class ScrapyConfig(ScrapyWrapperConfig):
	begin_urls = ["http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=C.BK04651&sty=FCOIATA&sortType=C&sortRule=-1&page=1&pageSize=1000&js=var%20quote_123%3d{rank:[(x)],pages:(pc)}&token=7bc05d0d4c3c22ef9fca8c2a912d779c&jsName=quote_123&_g=0.0603660640467345"]
	steps = {
		"begin": {
			'res': {
			    'parser': 'js-object',
				'selector_json': u'rank',
				'selector': lambda s, meta: s.split(',')[1],
				'next_step': 'content'
			}
		},
		"content": {
			'req': {
				'url': lambda url, meta: 'http://soft-f9.eastmoney.com/soft/gp67.php?code=' + str(url) + '02'
			},
			'res': {
				'selector_css': 'tr',
				'next_step': 'db'
			},
			'fields': [{
				'name': '$$StockCode'
			}]
		},
		"db": {
			'type': "db",
			'table_name': "PublicCompanyAgencyRating",
			'unique': ['CompanyID', 'RatingDate'],
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
				'name': "RatingDate",
				'selector_xpath': '//td[1]',
				'data_type': 'Date',
				'required': True,
				'mute_warnings': True
			}, {
				'name': 'AgencyName',
				'selector_xpath': '//td[2]',
				'required': True
			}, {
				'name': 'AnalystName',
				'selector_xpath': '//td[3]',
				'required': True
			}, {
				'name': 'Conclusion',
				'selector_xpath': '//td[4]',
				'required': True
			}
			]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

