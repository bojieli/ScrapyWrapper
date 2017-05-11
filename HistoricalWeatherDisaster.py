#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig

class ScrapyConfig(ScrapyWrapperConfig):
	begin_urls = ['http://map.kmzyw.com.cn/data/zaihai_list.jsp']
	steps = {
		"begin": {
			"req": {
				'method': 'post',
				'post_formdata': {
					'pzname': '',
					'type': '1',
					'starttime': '2014-01-01',
					'endtime': '2020-12-31'
				}
			},
			'res': [{
				'selector_json': 'msg',
				'next_step': 'db'
			}]
		},
		"db": {
			'type': "db",
			'table_name': "HistoricalWeatherDisaster",
			'unique': ['PublicationDate', 'Region', 'DisasterType'],
			'upsert': True,
			'fields': [{
				'name': "PublicationDate",
				'selector_json': 'Time'
			}, {
				'name': "$$City",
				'selector_json': 'City',
			}, {
				'name': "$$Province",
				'selector_json': 'Province',
			}, {
				'name': "$$County",
				'selector_json': 'County',
			}, {
				'name': 'RegionID',
				'reference': { 'field': '$$City', 'match': 'address' }
			}, {
				'name': 'Region',
				'selector': lambda _, meta: meta['$$Province'] + meta['$$City'] + meta['$$County'],
				'required': True
			}, {
				'name': "DisasterType",
				'selector_json': 'Disaster',
				'required': True
			}, {
				'name': "DisasterDescription",
				'selector_json': 'Addtion'
			}
			]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

