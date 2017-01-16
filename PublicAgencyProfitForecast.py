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
			'res': [{
			    'parser': 'js-object',
				'selector_json': u'rank',
				'selector': lambda s, meta: s.split(',')[1],
				'next_step': 'content1'
			}, {
			    'parser': 'js-object',
				'selector_json': u'rank',
				'selector': lambda s, meta: s.split(',')[1],
				'next_step': 'content2'
			}]
		},
		"content1": {
			'req': {
				'url': lambda url, meta: 'http://f10.eastmoney.com/f10_v2/BackOffice.aspx?command=RptEarningsForecastDetails&paramCode=' + str(url) + '02&paramNum=0&paramType='
			},
			'res': {
				'selector_css': 'tr',
				'next_step': 'table'
			},
			'fields': [{
				'name': '$$StockCode'
			}, {
				'name': 'ForecastType', 'value': '1'
			}]
		},
		"content2": {
			'req': {
				'url': lambda url, meta: 'http://f10.eastmoney.com/f10_v2/BackOffice.aspx?command=RptEarningsForecastDetails&paramCode=' + str(url) + '02&paramNum=1&paramType='
			},
			'res': {
				'selector_css': 'tr',
				'next_step': 'table'
			},
			'fields': [{
				'name': '$$StockCode'
			}, {
				'name': 'ForecastType', 'value': '2'
			}]
		},
		'table': {
			'type': 'intermediate',
			'res': {
				'selector_xpath': '//td[position() >= 3 and position() < 9]',
				'next_step': 'db'
			},
			'fields': [{
				'name': 'CompanyID',
				'reference': {
					'field': '$$StockCode',
					'table': 'PublicCompanyInfo',
					'remote_field': 'StockCode'
				},
				'required': True
			}, {
				'name': "PublicationDate",
				'selector_xpath': '//th',
				'data_type': 'Date',
				'required': True,
				'mute_warnings': True
			}, {
				'name': 'AgencyName',
				'selector_xpath': '//td[1]',
				'required': True
			}, {
				'name': 'AnalystName',
				'selector_xpath': '//td[2]',
				'required': True
			}, {
				'name': 'Conclusion',
				'selector_xpath': '//td[9]',
				'required': True
			}
			]
		},
		"db": {
			'type': "db",
			'table_name': "PublicAgencyProfitForecast",
			#'unique': ['CompanyID', 'PublicationDate', 'AgencyName', 'ForecastYear', 'ForecastType'],
			#'upsert': True,
			'fields': [{
				'name': 'ForecastYear',
				'selector': lambda _, meta: meta['$$record_count'] + 2015,
				'required': True
			}, {
				'name': 'ForecastFigure',
				'data_type': 'float',
				'required': True
			}]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

