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
				'url': lambda url, meta: 'http://soft-f9.eastmoney.com/soft/gp14.php?code=' + str(url) + '02'
			},
			'res': {
				'selector_table': True,
				'next_step': 'db'
			},
			'fields': [{
				'name': '$$StockCode'
			}]
		},
		"db": {
			'type': "db",
			'table_name': "PublicCompanyProfitTrend",
			'unique': ['CompanyID', 'PublicationDate'],
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
				'name': "PublicationDate",
				'selector_json': u'$$key',
				'data_type': 'Date',
				'required': True,
				'mute_warnings': True
			}, {
				'selector_json': u'单季度\\.销售毛利率(%)', 'name': 'QuarterlySaleGrossProfitMargin',
				'data_type': 'float'
			}, {
				'selector_json': u'单季度\\.销售净利率(%)', 'name': 'QuarterlySaleNetProfitRatio',
				'data_type': 'float'
			}, {
				'selector_json': u'单季度\\.摊薄净资产收益率ROE(%)', 'name': 'QuarterlyDilutedNetRoe',
				'data_type': 'float'
			}, {
				'selector_json': u'单季度\\.摊薄总资产净利率ROA(%)', 'name': 'QuarterlyDilutedRoa',
				'data_type': 'float'
			}, {
				'selector_json': u'单季度\\.营业总收入(元)', 'name': 'QuarterlyTotalOperatingIncome',
				'data_type': 'float'
			}, {
				'selector_json': u'单季度\\.营业总成本(元)', 'name': 'QuarterlyTotalOperatingCost',
				'data_type': 'float'
			}, {
				'selector_json': u'单季度\\.营业收入(元)', 'name': 'QuarterlyOperatingIncome',
				'data_type': 'float'
			}, {
				'selector_json': u'单季度\\.营业成本(元)', 'name': 'QuarterlyOperatingCost',
				'data_type': 'float'
			}, {
				'selector_json': u'单季度\\.营业利润(元)', 'name': 'QuarterlyOperatingProfit',
				'data_type': 'float'
			}, {
				'selector_json': u'单季度\\.利润总额(元)', 'name': 'QuarterlyTotalProfit',
				'data_type': 'float'
			}, {
				'selector_json': u'单季度\\.净利润(元)', 'name': 'QuarterlyNetProfit',
				'data_type': 'float'
			}, {
				'selector_json': u'季度\\.归属母公司股东的净利润(元)', 'name': 'QuarterlyNetProfitParentCompany',
				'data_type': 'float'
			}, {
				'selector_json': u'单季度\\.经营活动产生的现金流量(元)', 'name': 'QuarterlyOperatingCashFlow',
				'data_type': 'float'
			}, {
				'selector_json': u'单季度\\.投资活动产生的现金流量(元)', 'name': 'QuarterlyInvestmentCashFlow',
				'data_type': 'float'
			}, {
				'selector_json': u'单季度\\.筹资活动产生的现金流量(元)', 'name': 'QuarterlyFundRaiseCashFlow',
				'data_type': 'float'
			}, {
				'selector_json': u'单季度\\.现金及现金等价物净增加(元)', 'name': 'QuarterlyIncomingCashFlow',
				'data_type': 'float'
			}
			]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

