#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
import datetime

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
			'req': {
				'url': 'http://www.yt1998.com/price/historyPriceQ!getHistoryChandi.do',
				'method': 'post',
				'post_formdata': {
					'ycnam': lambda _, meta: meta['$$TcmName'],
					'market': '1'
				}
			},
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
				'name': 'MarketID',
				'reference': {
					'field': '$$MarketName',
					'table': 'TcmMarket',
					'remote_field': 'MarketName',
					'remote_id_field': 'ID',
					'match': 'wildcard'
				},
			}, {
				'name': '$$MarketName',
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
					'chandi': lambda _, meta: meta['$$MarketName'],
					'market': '1'
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
					'chandi': lambda _, meta: meta['$$MarketName'],
					'guige': lambda _, meta: meta['Specification'],
					'market': '1'
				},
			},
			'res': {
				'selector_json': 'data',
				'next_step': 'db'
			}
		},
		"db": {
			'type': "db",
			'table_name': "TcmMarketMonthlyPrice",
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
			}, {
				'name': 'PriceSource',
				'value': '3'
			}]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

