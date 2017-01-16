#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
import datetime

class ScrapyConfig(ScrapyWrapperConfig):
	def url_generator(self):
		for i in range(1,2000):
			yield str(i)

	begin_urls = url_generator

	steps = {
		"begin": {
			'req': {
				'url': 'http://www.zyctd.com/Breeds/GetMNameByMBID',
				'method': 'post',
				'post_formdata': {
					'MBID': lambda url, _: url
				}
			},
			'res': {
				'selector_json': 'Data',
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
			}, {
				'name': '$$TcmName',
				'selector_json': 'MName',
				'required': True
			}, {
				'name': '$$MTypeID',
				'selector_json': 'MTypeID'
			}, {
				'name': '$$MBID',
				'selector_json': 'MBID',
				'required': True
			}]
		},
		'area': {
			'req': {
				'url': 'http://www.zyctd.com/Breeds/GetAreaByMBID',
				'method': 'post',
				'post_formdata': {
					'MBID': lambda _, meta: meta['$$MBID'],
					'MAreaTypeID': '2'
				}
			},
			'res': {
				'selector_json': 'Data',
				'next_step': 'parse_area',
			}
		},
		'parse_area': {
			'type': 'intermediate',
			'res': {
				'next_step': 'spec'
			},
			'fields': [{
				'name': '$$MAreaID',
				'selector_json': 'MAreaID',
				'required': True
			}, {
				'name': 'PlaceOfOrigin',
				'selector_json': 'MArea',
				'data_postprocessor': lambda d,_: d.replace(u'药市', ''),
				'required': True
			}, {
				'name': "PlaceOfOriginID",
				'reference': { 'field': 'PlaceOfOrigin', 'table': 'TB_Addresses', 'remote_field': 'Name', 'remote_id_field': 'PID', 'match': 'lpm' }
			}]
		},
		'spec': {
			'req': {
				'url': 'http://www.zyctd.com/Breeds/GetSpecByAreaID',
				'method': 'post',
				'post_formdata': {
					'MBID': lambda _, meta: meta['$$MBID'],
					'MAreaID': lambda _, meta: meta['$$MAreaID']
				},
			},
			'res': {
				'selector_json': 'Data',
				'next_step': 'parse_spec'
			}
		},
		'parse_spec': {
			'type': 'intermediate',
			'fields': [{
				'name': 'Specification',
				'selector_json': 'MSpec',
				'required': True
			}, {
				'name': '$$mid',
				'selector_json': 'mid',
				'required': True
			}],
			'res': {
				'next_step': 'price'
			}
		},
		'price': {
			'req': {
				'url': 'http://www.zyctd.com/Breeds/GetPriceTable',
				'method': 'post',
				'post_formdata': {
					'mid': lambda _, meta: meta['$$mid']
				},
			},
			'res': {
				'selector_json': 'Data',
				'next_step': 'year_price'
			}
		},
		'year_price': {
			'type': 'intermediate',
			'res': {
				'selector_json': 'ListTdMonthPrice',
				'next_step': 'month_price'
			},
			'fields': [{
				'name': '$$Year',
				'selector_json': 'Year',
				'required': True
			}]
		},
		"month_price": {
			'type': "db",
			'table_name': "TcmPlaceOfOriginMonthlyPrice",
			'unique': ['TcmID', 'Specification', 'PlaceOfOrigin', 'CurrentDate', 'PriceSource'],
			'upsert': True,
			'fields': [{
				'name': '$$Month',
				'selector_json': 'Month',
				'required': True
			}, {
				'name': 'CurrentDate',
				'selector': lambda _, meta: meta['$$Year'] + '-' + meta['$$Month'] + '-' + '01',
				'validator': lambda _, meta: datetime.date(int(meta['$$Year']), int(meta['$$Month']), 1) <= datetime.date.today(),
				'data_type': 'Date',
				'required': True
			}, {
				'name': 'Price',
				'selector_json': 'Price',
				'required': True
			}, {
				'name': 'PriceSource',
				'value': '1'
			}]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

