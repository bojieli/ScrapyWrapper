#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
import datetime

class ScrapyConfig(ScrapyWrapperConfig):
	begin_urls = ["http://www.yt1998.com/price/nowDayPriceQ!getPriceList.do?random=0.02907702647346211&ycnam=&market=&leibie=&istoday=&spices=&paramName=&paramValue=&pageIndex=1&pageSize=10000"]

	steps = {
		"begin": {
			'res': {
				'selector_json': 'data',
				'next_step': 'db_day',
			}
		},
		"db_day": {
			'type': "db",
			'table_name': "TcmPlaceOfOriginPrice",
			'unique': ['TcmID', 'Specification', 'PlaceOfOrigin', 'CurrentDate', 'PriceSource'],
			'upsert': True,
			'fields': [{
				'name': 'CurrentDate',
				'value': datetime.datetime.today().strftime('%Y-%m-%d')
			}, {
				'name': 'Specification',
				'selector_json': 'guige',
				'required': True
			}, {
				'name': 'Price',
				'selector_json': 'pri',
				'data_type': 'float',
				'required': True
			}, {
				'name': 'PlaceOfOrigin',
				'selector_json': 'chandi',
				'required': True
			}, {
				'name': "PlaceOfOriginID",
				'reference': { 'field': 'PlaceOfOrigin', 'table': 'TB_Addresses', 'remote_field': 'Name', 'remote_id_field': 'PID', 'match': 'lpm' }
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
				'selector_json': 'ycnam',
				'required': True
			}, {
				'name': 'IncreaseFromLastWeek',
				'selector_json': 'zhouduibi',
				'data_type': 'float',
				'required': True
			}, {
				'name': 'IncreaseFromLastMonth',
				'selector_json': 'yueduibi',
				'data_type': 'float',
				'required': True
			}, {
				'name': 'IncreaseFromLastYear',
				'selector_json': 'nianduibi',
				'data_type': 'float',
				'required': True
			}, {
				'name': 'PriceSource',
				'value': '3'
			}]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

