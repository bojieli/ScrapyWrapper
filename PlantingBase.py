#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
import json

import urllib2
req = urllib2.Request('http://map.kmzyw.com.cn/data/get_map_quanguo.jsp', None, {'User-Agent' : 'Mozilla/5.0'})
json_obj = json.loads(urllib2.urlopen(req).read())
def sanitize(p):
	return p.rstrip(u'省').rstrip(u'市')
province_list = [ sanitize(o['Province']) for o in json_obj['msg'] ]
if len(province_list) == 0:
	raise 'Error loading province list'
print(province_list)

def getProvince(s):
	for p in province_list:
		if s.startswith(p):
			return p
	return None

class ScrapyConfig(ScrapyWrapperConfig):
	begin_urls = ["http://map.kmzyw.com.cn/data/get_map_list_pz.jsp"]
	steps = {
		"begin": {
			'req': {
				'method': 'post',
				'post_formdata': {'sheng':'', 'shi':'', 'xian':'', 'isgap':'0'}
			},
			'res': [{
				'selector_json': 'msg',
				'next_step': 'db'
			}]
		},
		"db": {
			'type': "db",
			'table_name': "PlantingBase",
			'unique': ['TcmName', 'PlantingBaseName'],
			'upsert': True,
			'fields': [{
				'name': "TcmID",
				'reference': {
					'field': 'TcmName',
					'table': 'TB_Resources_TraditionalChineseMedicinalMaterials',
					'remote_field': 'MedicineName',
					'remote_id_field': 'ResID',
					'insert_if_not_exist': True
				}
			}, {
				'name': "TcmName",
				'selector_json': 'MedicineName',
				'required': True
			}, {
				'name': "ProvinceID",
				'reference': { 'field': 'Province', 'match': 'address' }
			}, {
				'name': "Province",
				'selector_json': 'BaseName',
				'data_postprocessor': lambda d,_: getProvince(d)
			}, {
				'name': "PlantingBaseName",
				'selector_json': 'BaseName'
			}, {
				'name': 'WeatherCondition',
				'selector_json': 'Climate'
			}, {
				'name': 'GenuineProducingArea',
				'selector_json': 'IsNotedPlace'
			}, {
				'name': 'GapBase',
				'selector_json': 'HasGAP'
			}, {
				'name': 'TotalProductionVolume',
				'selector_json': 'Area',
				'data_type': 'float'
			}, {
				'name': 'ProductionPerHectare',
				'selector_json': 'UnitProduction',
				'data_type': 'float'
			}, {
				'name': 'TcmPrice',
				'selector_json': 'Price',
				'data_type': 'float'
			}, {
				'name': 'SourceDataCollectionTime',
				'selector_json': 'Time',
				'data_type': 'Date'
			}
			]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

