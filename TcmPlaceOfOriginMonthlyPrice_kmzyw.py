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
				'next_step': 'list'
			}
		},
		"list": {
			'type': 'intermediate',
			'fields': [{
				'name': 'TcmID',
				'reference': {
					'field': 'TcmName',
					'table': 'TB_Resources_TraditionalChineseMedicinalMaterials',
					'remote_field': 'MedicineName',
					'remote_id_field': 'ResID',
					'insert_if_not_exist': True
				},
				'required': True
			}, {
				'name': 'TcmName',
				'selector_json': 'drug_name',
				'required': True
			}],
			'res': {
				'selector_json': 'drug_name',
				'data_postprocessor': lambda _,meta: 'http://www.kmzyw.com.cn/bzjsp/Biz_price_history/price_history_search.jsp?name=' + urllib.quote(urllib.quote(meta['TcmName'].encode('utf-8'))),
				'next_step': 'content'
			}
		},
		"content": {
			'res': {
				'selector_regex': '\$\(".movements"\).parent\(\).after\("([^"]*)"\);',
				'next_step': 'tables',
				'required': True
			}
		},
		"tables": {
			'type': 'intermediate',
			'res': {
				'selector_xpath': '//section',
				'next_step': 'table_title'
			}
		},
		"table_title": {
			'type': 'intermediate',
			'res': {
				'selector_xpath': '//table//tr',
				'next_step': 'year_price'
			},
			'fields': [{
				'name': 'Specification',
				'selector_xpath': '//p',
				'selector_regex': u'规格：(.*)，产地',
				'required': True
			}, {
				'name': 'PlaceOfOrigin',
				'selector_xpath': '//p',
				'selector_regex': u'产地：(.*)',
				'required': True
			}, {
				'name': "PlaceOfOriginID",
				'reference': { 'field': 'PlaceOfOrigin', 'match': 'address' }
			}]
		},
		"year_price": {
			'type': 'intermediate',
			'res': {
				'selector_xpath': '//td[not(@class="ths")]',
				'next_step': 'month_price'
			},
			'fields': [{
				'name': '$$Year',
				'selector_xpath': '//td[@class="ths"]',
				'required': True
			}]
		},
		"month_price": {
			'type': "db",
			'table_name': "TcmPlaceOfOriginMonthlyPrice",
			'unique': ['CurrentDate', 'Specification', 'PlaceOfOrigin', 'TcmID'],
			'upsert': True,
			'fields': [{
				'name': '$$Month',
				'selector': lambda _, meta: str(int(meta['$$record_count']) + 1),
				'required': True
			}, {
				'name': 'CurrentDate',
				'selector': lambda _, meta: meta['$$Year'] + '-' + meta['$$Month'] + '-' + '01',
				'validator': lambda _, meta: datetime.date(int(meta['$$Year']), int(meta['$$Month']), 1) <= datetime.date.today(),
				'data_type': 'Date',
				'required': True
			}, {
				'name': 'Price',
				'data_type': 'float',
				'required': True
			}]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

