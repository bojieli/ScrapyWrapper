#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
import datetime

class ScrapyConfig(ScrapyWrapperConfig):
	def url_generator(self):
		for i in range(1,2000):
			yield "http://www.zyctd.com/jh" + str(i) + ".html"

	begin_urls = url_generator

	steps = {
		"begin": {
			'res': {
				'selector_xpath': '//body',
				'next_step': 'content',
			}
		},
		"content": {
			'type': 'intermediate',
			'res': [{
				'selector_xpath': '//*[@id="jg"]//table[2]//tr',
				'next_step': 'TcmPlaceOfOriginPrice'
			},
			{
				'selector_xpath': '//*[@id="jg"]//table[1]//tr',
				'next_step': 'TcmMarketDailyPrice'
			}],
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
				'selector_xpath': '//div[@class="breedtitle"]//h1',
				'selector_regex': '# (.*)',
				'required': True
			}]
		},
		"TcmMarketDailyPrice": {
			'type': 'db',
			'table_name': 'TcmMarketDailyPrice',
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
				'name': '$$MarketName',
				'selector_xpath': '//td[2]',
				'required': True
			}, {
				'name': 'Specification',
				'selector_xpath': '//td[1]',
				'selector_regex': '([^ ]*)', # remove province
				'required': True
			}, {
				'name': 'CurrentDate',
				'value': datetime.datetime.today().strftime('%Y-%m-%d')
			}, {
				'name': 'Price',
				'selector_xpath': '//td[3]',
				'data_type': 'float',
				'required': True
			}, {
				'name': 'IncreaseFromLastWeek',
				'selector_xpath': '//td[4]',
				'data_type': 'float'
			}, {
				'name': 'IncreaseFromLastMonth',
				'value': None,
			}, {
				'name': 'IncreaseFromLastYear',
				'value': None
			}]
		},
		"TcmPlaceOfOriginPrice": {
			'type': "db",
			'table_name': "TcmPlaceOfOriginPrice",
			'fields': [{
				'name': 'PlaceOfOrigin',
				'selector_xpath': '//td[2]',
				'required': True
			}, {
				'name': 'Specification',
				'selector_xpath': '//td[1]',
				'required': True
			}, {
				'name': 'CurrentDate',
				'value': datetime.datetime.today().strftime('%Y-%m-%d')
			}, {
				'name': 'Price',
				'selector_xpath': '//td[3]',
				'data_type': 'float',
				'required': True
			}, {
				'name': 'IncreaseFromLastWeek',
				'selector_xpath': '//td[4]',
				'data_type': 'float'
			}, {
				'name': 'IncreaseFromLastMonth',
				'value': None,
			}, {
				'name': 'IncreaseFromLastYear',
				'value': None
			}, {
				'name': 'CurrentTrend',
				'selector_xpath': '//td[5]'
			}]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

