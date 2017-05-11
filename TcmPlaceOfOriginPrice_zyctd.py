#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
import datetime

class ScrapyConfig(ScrapyWrapperConfig):
	def url_generator(self):
		for i in range(1,100):
			yield "http://www.zyctd.com/jiage/8-0-0-" + str(i) + ".html"

	begin_urls = url_generator

	steps = {
		"begin": {
			'req': {'webview': True},
			'res': {
				'selector_xpath': '//ul[@class="priceTableRows"]/li',
				'next_step': 'TcmPlaceOfOriginPrice',
				'required': True
			}
		},
		"TcmPlaceOfOriginPrice": {
			'type': "db",
			'table_name': "TcmPlaceOfOriginPrice",
			'unique': ['TcmID', 'Specification', 'PlaceOfOrigin', 'PriceSource', 'CurrentDate'],
			'upsert': True,
			'fields': [{
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
				'selector_xpath': '//span[1]',
				'required': True
			}, {
				'name': 'PlaceOfOrigin',
				'selector_xpath': '//span[3]',
				'required': True
			}, {
				'name': "PlaceOfOriginID",
				'reference': { 'field': 'PlaceOfOrigin', 'match': 'address' }
			}, {
				'name': 'Specification',
				'selector_xpath': '//span[2]',
				'required': True
			}, {
				'name': 'CurrentDate',
				'value': datetime.datetime.today().strftime('%Y-%m-%d')
			}, {
				'name': 'Price',
				'selector_xpath': '//span[4]',
				'data_type': 'float',
				'required': True
			}, {
				'name': 'IncreaseFromLastWeek',
				'selector_xpath': '//span[6]',
				'data_type': 'percentage'
			}, {
				'name': 'IncreaseFromLastMonth',
				'selector_xpath': '//span[7]',
				'data_type': 'percentage'
			}, {
				'name': 'IncreaseFromLastYear',
				'selector_xpath': '//span[8]',
				'data_type': 'percentage'
			}, {
				'name': 'CurrentTrend',
				'selector_xpath': '//span[5]',
				'required': True
			}, {
				'name': 'PriceSource',
				'value': '1'
			}],
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

