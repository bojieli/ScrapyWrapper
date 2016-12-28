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
			    'parser': 'js-string',
				'selector': lambda s, meta: s.split(',')[1],
				'next_step': 'content'
			}
		},
		"content": {
			'req': {
				'url': lambda url, meta: 'http://f10.eastmoney.com/f10_v2/FinanceAnalysis.aspx?code=sz' + str(url) + '#zyzb-0'
			},
			'res': {
				'selector_regex': "SwitchZYZB\('([0-9]*)'",
				'keep_html_tags': False,
				'next_step': 'table'
			},
			'fields': [{
				'name': '$$StockCode'
			}]
		},
		"table": {
			'req': {
				'url': lambda url, meta: 'http://f10.eastmoney.com/f10_v2/BackOffice.aspx?command=RptF10MainTarget_1&code=' + str(url) + '&num=1000'
			},
			'res': {
				'selector_matrix': {'has_header': True},
				'next_step': 'db'
			}
		},
		"db": {
			'type': "db",
			'table_name': "PublicCompanyKeyNumber",
			'fields': [{
				'name': 'CompanyID',
				'reference': {
					'field': '$$StockCode',
					'table': 'PublicCompanyInfo',
					'remote_field': 'StockCode'
				},
				'required': True
			}, {
				'name': "ReportDate",
				'selector_xpath': '//th',
				'data_type': 'Date',
				'required': True
			}, {
				'name': 'BasicEarningPerShare',
				'selector_xpath': '//td[1]',
				'data_type': 'float'
			}, {
				'name': 'EarningDeductionPerShare',
				'selector_xpath': '//td[2]',
				'data_type': 'float'
			}, {
				'name': 'DilutedEarningPerShare',
				'selector_xpath': '//td[3]',
				'data_type': 'float'
			}, {
				'name': 'NetEarningPerShare',
				'selector_xpath': '//td[4]',
				'data_type': 'float'
			}, {
				'name': 'NetEarningPerShareChange',
				'selector_xpath': '//td[5]',
				'data_type': 'float'
			}, {
				'name': 'NetEarningPerShareMat',
				'selector_xpath': '//td[6]',
				'data_type': 'float'
			}, {
				'name': 'WeightedReturnOnEquity',
				'selector_xpath': '//td[7]',
				'data_type': 'float'
			}, {
				'name': 'DilutedReturnOnEquity',
				'selector_xpath': '//td[8]',
				'data_type': 'float'
			}, {
				'name': 'GrossProfitRate',
				'selector_xpath': '//td[9]',
				'data_type': 'float'
			}, {
				'name': 'ActualTaxRate',
				'selector_xpath': '//td[10]',
				'data_type': 'float'
			}, {
				'name': 'EstimatedOperatingIncome',
				'selector_xpath': '//td[11]',
				'data_type': 'float'
			}
			]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

