#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
import datetime

class ScrapyConfig(ScrapyWrapperConfig):
	def url_generator(self):
		for i in range(1,250):
			yield "http://www.zyctd.com/jiage/1-0-0-" + str(i) + ".html"

	#crawlera_enabled = True
	begin_urls = url_generator

	steps = {
		"begin": {
			'res': {
				'selector_css': 'ul.priceTableRows li',
				'next_step': 'TcmMarketDailyPrice',
			}
		},
		"TcmMarketDailyPrice": {
			'type': 'db',
			'table_name': 'TcmMarketDailyPrice',
			'unique': ['TcmID', 'Specification', 'MarketID', 'CurrentDate'],
			'upsert': True,
			'fields': [{
				'name': 'MarketID',
				'reference': {
					'field': '$$MarketName',
					'table': 'TcmMarket',
					'remote_field': 'MarketName',
					'remote_id_field': 'ID',
					'match': 'wildcard'
				},
				'required': True
			}, {
				'name': 'TcmID',
				'reference': {
					'field': '$$TcmName',
					'table': 'TB_Resources_TraditionalChineseMedicinalMaterials',
					'remote_field': 'MedicineName',
					'remote_id_field': 'ResID'
				},
				'required': True
			}, {
				'name': '$$TcmName',
				'selector_css': 'span.w1 a',
				'required': True
			}, {
				'name': '$$MarketName',
				'selector_css': 'span.w9',
				'required': True
			}, {
				'name': 'Specification',
				'selector_css': 'span.w2',
				'required': True
			}, {
				'name': 'CurrentDate',
				'value': datetime.datetime.today().strftime('%Y-%m-%d')
			}, {
				'name': 'Price',
				'selector_css': 'span.w3',
				'data_type': 'float',
				'required': True
			}, {
				'name': 'IncreaseFromLastWeek',
				'selector_css': 'span.w5',
				'data_type': 'float',
				'required': True
			}, {
				'name': 'IncreaseFromLastMonth',
				'selector_css': 'span.w6',
				'data_type': 'float',
				'required': True
			}, {
				'name': 'IncreaseFromLastYear',
				'selector_css': 'span.w7',
				'data_type': 'float',
				'required': True
			}]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

