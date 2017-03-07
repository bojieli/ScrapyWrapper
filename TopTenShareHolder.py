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
				'url': lambda url, meta: 'http://f10.eastmoney.com/f10_v2/ShareholderResearch.aspx?code=sz' + str(url)
			},
			'res': {
				'selector_xpath': '//body',
				'next_step': 'page'
			},
			'fields': [{
				'name': '$$StockCode'
			}]
		},
		"page": {
			'type': 'intermediate',
			'res': {
				'selector_xpath': '//*[@id="TTS_Table_Div"]/table[1]/tr',
				'next_step': 'db'
			},
			'fields': [{
				'name': "ReportDate",
				'selector_xpath': '//li[@onclick="TTS_ChangeTab(0,this);"]',
				'data_type': 'Date',
				'required': True
			}]
		},
		"db": {
			'type': "db",
			'table_name': "TopTenShareHolder",
			'unique': ['CompanyID', 'ReportDate', 'ShareHolderName'],
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
				'name': "ShareHolderName",
				'selector_xpath': '//td[1]',
				'required': True
			}, {
				'name': "ShareType",
				'selector_xpath': '//td[2]'
			}, {
				'name': "NumberOfShare",
				'selector_xpath': '//td[3]',
				'data_type': 'int',
				'required': True
			}, {
				'name': "PercentOfTotalShare",
				'selector_xpath': '//td[4]',
				'data_type': 'percentage',
				'required': True
			}, {
				'name': "ChangeInShare",
				'selector_xpath': '//td[5]'
			}, {
				'name': "ChangePercentage",
				'selector_xpath': '//td[6]'
			}
			]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

