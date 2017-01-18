#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
import datetime

def PMIndexToCategory(index):
	index = int(index)
	if index <= 50:
		return u'优'
	if index <= 100:
		return u'良'
	if index <= 150:
		return u'轻度污染'
	if index <= 200:
		return u'中度污染'
	if index <= 300:
		return u'重度污染'
	return u'严重污染'

class ScrapyConfig(ScrapyWrapperConfig):
	begin_urls = ["http://106.37.208.228:8082/Home/Default"]
	steps = {
		"begin": {
			'res': {
			    'selector_regex': 'var cities = \[(.*)\]\[0\]',
				'next_step': 'content'
			}
		},
		"content": {
			'type': 'intermediate',
			'res': {
				'selector_json': '',
				'next_step': 'db'
			}
		},
		"db": {
			'type': "db",
			'unique': ['PublicationDate', 'ForecastDate', 'Region'],
			'upsert': False,
			'table_name': "AirQualityForecast",
			'fields': [{
				'name': "PublicationDate",
				'value': datetime.datetime.now().strftime('%Y-%m-%d'),
				'data_type': 'Date'
			}, {
				'name': "ForecastDate",
				'value': (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d'),
				'data_type': 'Date'
			}, {
				'name': "RegionID",
				'reference': { 'field': 'Region', 'table': 'TB_Addresses', 'remote_field': 'Name', 'remote_id_field': 'PID', 'match': 'lpm' }
			}, {
				'name': "Region",
				'selector_json': 'Name',
				'required': True
			}, {
				'name': "PMIndexLowerLimit",
				'selector_json': 'AirIndex_From',
				'required': True
			}, {
				'name': "PMIndexUpperLimit",
				'selector_json': 'AirIndex_To',
				'required': True
			}, {
				'name': "PMCategoryLowerLimit",
				'selector_json': 'AirIndex_From',
				'data_postprocessor': lambda i,_: PMIndexToCategory(i),
				'required': True
			}, {
				'name': "PMCategoryUpperLimit",
				'selector_json': 'AirIndex_To',
				'data_postprocessor': lambda i,_: PMIndexToCategory(i),
				'required': True
			}, {
				'name': "PMTwoDotFive",
				'selector_json': 'PrimaryPollutant',
				'data_postprocessor': lambda d, meta: '1' if 'PM2.5' in d else '0'
			}, {
				'name': "PMTen",
				'selector_json': 'PrimaryPollutant',
				'data_postprocessor': lambda d, meta: '1' if 'PM10' in d else '0'
			}
			]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

