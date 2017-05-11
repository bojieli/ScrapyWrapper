#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
import datetime

def gen_area_req(url, meta):
	for market in range(1,5):
		meta['$$MarketName'] = ['',u'亳州',u'安国',u'成都',u'玉林'][market]
		meta['$$Market'] = str(market)
		yield {
				'url': 'http://www.yt1998.com/price/historyPriceQ!getHistoryChandi.do',
				'method': 'post',
				'post_formdata': {
					'ycnam': meta['$$TcmName'],
					'market': str(market)
				},
			}
	

class ScrapyConfig(ScrapyWrapperConfig):
	begin_urls = ["http://www.yt1998.com/price/nowDayPriceQ!getPriceList.do?random=0.3043301286963105&ycnam=&market=1&leibie=&istoday=&spices=&paramName=&paramValue=&pageIndex=0&pageSize=10000"]

	steps = {
		"begin": {
			'res': {
				'selector_json': 'data',
				'next_step': 'parse_name',
			}
		},
		"parse_name": {
			'type': 'intermediate',
			'res': {
				'next_step': 'area'
			},
			'fields': [{
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
			}]
		},
		'area': {
			'req': gen_area_req,
			'res': {
				'selector_json': 'data',
				'next_step': 'parse_area',
			}
		},
		'parse_area': {
			'type': 'intermediate',
			'res': {
				'next_step': 'spec'
			},
			'fields': [{
				'name': "PlaceOfOriginID",
				'reference': { 'field': 'PlaceOfOrigin', 'match': 'address' }
			}, {
				'name': 'PlaceOfOrigin',
				'selector_json': 'chandi',
				'required': True
			}]
		},
		'spec': {
			'req': {
				'url': 'http://www.yt1998.com/price/historyPriceQ!getHistoryGuige.do',
				'method': 'post',
				'post_formdata': {
					'ycnam': lambda _, meta: meta['$$TcmName'],
					'chandi': lambda _, meta: meta['PlaceOfOrigin'],
					'market': lambda _, meta: meta['$$Market'],
				},
			},
			'res': {
				'selector_json': 'data',
				'next_step': 'parse_spec'
			}
		},
		'parse_spec': {
			'type': 'intermediate',
			'fields': [{
				'name': 'Specification',
				'selector_json': 'guige',
				'required': True
			}],
			'res': {
				'next_step': 'price'
			}
		},
		'price': {
			'req': {
				'url': 'http://www.yt1998.com/price/historyPriceQ!getHistoryPrice.do',
				'method': 'post',
				'post_formdata': {
					'ycnam': lambda _, meta: meta['$$TcmName'],
					'chandi': lambda _, meta: meta['PlaceOfOrigin'],
					'guige': lambda _, meta: meta['Specification'],
					'market': lambda _, meta: meta['$$Market'],
				},
			},
			'res': [{
				'selector_json': 'data',
				'next_step': 'db_month'
			}, {
				'selector_json': 'data',
				'next_step': 'db_day'
			}]
		},
		"db_month": {
			'type': "db",
			'table_name': "TcmPlaceOfOriginMonthlyPrice",
			'unique': ['TcmID', 'Specification', 'PlaceOfOrigin', 'CurrentDate', 'PriceSource'],
			'upsert': True,
			'fields': [{
				'name': 'CurrentDate',
				'selector_json': 'Date_time',
				# only get the 1st day price per month
				'data_validator': lambda datestr, _: datestr.split('-')[2] == '01' and datetime.date(*(map(int, datestr.split('-')))) <= datetime.date.today(),
				'data_type': 'Date',
				'required': True
			}, {
				'name': 'Price',
				'selector_json': 'DayCapilization',
				'data_type': 'float',
				'required': True
			}, {
				'name': 'PriceSource',
				'value': '3'
			}]
		},
		"db_day": {
			'type': "db",
			'table_name': "TcmPlaceOfOriginMonthlyPrice",
			'unique': ['TcmID', 'Specification', 'PlaceOfOrigin', 'CurrentDate'],
			'upsert': True,
			'fields': [{
				'name': 'CurrentDate',
				'selector_json': 'Date_time',
				'data_type': 'Date',
				'required': True
			}, {
				'name': 'Price',
				'selector_json': 'DayCapilization',
				'data_type': 'float',
				'required': True
			}]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

