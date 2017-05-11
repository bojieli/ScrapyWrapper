#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
import urllib
import datetime

class ScrapyConfig(ScrapyWrapperConfig):
	def url_generator(self):
		for i in range(1,60):
			yield str(i)

	begin_urls = url_generator

	steps = {
		"begin": {
			'req': {
				'url': 'http://www.kmzyw.com.cn/bzjsp/biz_price_search/price_index_search.jsp',
				'method': 'post',
				'post_formdata': {
					'pagecode': lambda u,_: u
				}
			},
			'res': {
				'selector_json': 'rows',
				'next_step': 'day_price'
			}
		},
		"day_price": {
			'type': "db",
			'table_name': "TcmPlaceOfOriginPrice",
			'unique': ['TcmID', 'Specification', 'PlaceOfOrigin', 'CurrentDate', 'PriceSource'],
			'upsert': True,
			'fields': [{
				'name': 'CurrentDate',
				'value': datetime.datetime.today().strftime('%Y-%m-%d')
			}, {
				'name': 'Price',
				'selector_json': 'price',
				'data_type': 'float',
				'required': True
			}, {
				'name': 'TcmID',
				'reference': {
					'field': '$$TcmName',
					'table': 'TB_Resources_TraditionalChineseMedicinalMaterials',
					'remote_field': 'MedicineName',
					'remote_id_field': 'ResID',
					'insert_if_not_exist': True
				},
				'required': True
			}, {
				'name': '$$TcmName',
				'selector_json': 'drug_name',
				'required': True
			}, {
				'name': 'Specification',
				'selector_json': 'standards',
				'required': True
			}, {
				'name': "PlaceOfOriginID",
				'reference': { 'field': 'PlaceOfOrigin', 'match': 'address' }
			}, {
				'name': 'PlaceOfOrigin',
				'selector_json': 'origin',
				'required': True
			}, {
				'name': 'IncreaseFromLastWeek',
				'value': None
			}, {
				'name': 'IncreaseFromLastMonth',
				'selector_json': 'month_cal',
				'data_type': 'float',
				'data_postprocessor': lambda d,_: str(float(d)*100),
				'required': True
			}, {
				'name': 'IncreaseFromLastYear',
				'selector_json': 'year_cal',
				'data_type': 'float',
				'data_postprocessor': lambda d,_: str(float(d)*100),
				'required': True
			}, {
				'name': 'PriceSource',
				'value': '2'
			}]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

