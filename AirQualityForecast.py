#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
import datetime

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
			'table_name': "AirQualityForecast",
			'fields': [{
				'name': "PublicationDate",
				'value': datetime.datetime.now().strftime('%Y-%m-%d'),
				'data_type': 'Date'
			}, {
				'name': "ForecastDate",
				'value': datetime.datetime.now().strftime('%Y-%m-%d'),
				'data_type': 'Date'
			}, {
				'name': "RegionID",
				'reference': { 'field': 'SourceLocation', 'table': 'TB_Addresses', 'remote_field': 'Name', 'remote_id_field': 'PID', 'match': 'lpm' }
			}, {
				'name': "Region",
				'selector_json': 'Name',
				'required': True
			}, {
				'name': "PMIndexLowerLimit",
				'selector_json': 'AirIndex_From',
				'required': True
			}, {
				'name': "PMCategoryUpperLimit",
				'selector_json': 'AirIndex_To',
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

