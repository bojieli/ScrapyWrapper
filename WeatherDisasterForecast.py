#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig

class ScrapyConfig(ScrapyWrapperConfig):
	begin_urls = ["http://www.weather.com.cn/alarm/newalarmlist.shtml"]
	steps = {
		"begin": {
			'res': [{
				'selector_css': 'ul.dDUl li',
				'next_step': 'db'
			},
			{
				'selector_href_text_contains': u'下一页',
				'next_step': 'begin'
			}]
		},
		"db": {
			'type': "db",
			'table_name': "WeatherDisasterForecast",
			'fields': [{
				'name': "PublicationDate",
				'selector_css': 'span.dTime',
				'required': True
			}, {
				'name': "RegionID",
				'reference': {
					'field': 'Region',
					'table': 'TB_Addresses',
					'remote_field': 'Name',
					'remote_id_field': 'PID',
					'match': 'lpm'
				}
			}, {
				'name': "Region",
				'selector_xpath': '//a',
				'selector_regex': '(.*)气象台',
				'required': True
			}, {
				'name': "DisasterForecastType",
				'selector_xpath': '//a',
				'selector_regex': u'气象台发布(.*).色预警',
				'required': True
			}, {
				'name': "DisasterForecastLevel",
				'selector_xpath': '//a',
				'selector_regex': u'(.)色预警',
				'required': True
			}
			]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

