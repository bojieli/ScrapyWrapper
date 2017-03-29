#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
import json

def typemap(t):
	types = {"01":u"台风","02":u"暴雨","03":u"暴雪","04":u"寒潮","05":u"大风","06":u"沙尘暴","07":u"高温","08":u"干旱","09":u"雷电","10":u"冰雹","11":u"霜冻","12":u"大雾","13":u"霾","14":u"道路结冰","91":u"寒冷","92":u"灰霾","93":u"雷雨大风","94":u"森林火险","95":u"降温","96":u"道路冰雪","97":u"干热风","98":u"低温","99":u"空气重污染"}
	if t in types:
		return types[t]
	else:
		return None

def colormap(color):
	colors = {"01":u"蓝色","02":u"黄色","03":u"橙色","04":u"红色","91":u"白色"}
	if color in colors:
		return colors[color]
	else:
		return None

class ScrapyConfig(ScrapyWrapperConfig):
	begin_urls = ["http://product.weather.com.cn/alarm/grepalarm_cn.php?_=1483429886627"]
	steps = {
		"begin": {
			"req": {
				"headers": {"Referer": "http://www.weather.com.cn/alarm/newalarmlist.shtml"}
			},
			'res': {
				'parser': 'js-object',
				'selector_json': 'data',
				'next_step': 'db'
			}
		},
		"db": {
			'type': "db",
			'table_name': "WeatherDisasterForecast",
			'unique': ['PublicationDate', 'Region', 'DisasterForecastType'],
			'upsert': True,
			'fields': [{
				'name': "PublicationDate",
				'selector': lambda d, meta: json.loads(d)[1].split('-')[1],
				'data_type': 'Date',
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
				'selector': lambda d, meta: json.loads(d)[0],
				'required': True
			}, {
				'name': "DisasterForecastType",
				'selector': lambda d, meta: typemap(json.loads(d)[1].split('-')[2][0:2]),
				'required': True
			}, {
				'name': "DisasterForecastLevel",
				'selector': lambda d, meta: colormap(json.loads(d)[1].split('-')[2][2:4]),
				'required': True
			}
			]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

