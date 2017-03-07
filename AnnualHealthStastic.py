#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
import re
import json
import demjson
import urllib

def get_code_mapping(text, meta):
	obj = demjson.decode(text)
	mapping = {}
	try:
		for zb in obj['returndata']['wdnodes'][0]['nodes']:
			mapping[zb['code']] = zb
		meta['$$mapping_code_to_zb'] = mapping
	except:
		print(obj)
	return text

class ScrapyConfig(ScrapyWrapperConfig):
	begin_urls = ['A0O']
	steps = {
		"begin": {
			'req': {
				'url': 'http://data.stats.gov.cn/easyquery.htm',
				'method': 'post',
				'post_formdata': {
					'id': lambda url,_: url,
					'dbcode': 'hgnd',
					'wdcode': 'zb',
					'm': 'getTree'
				}
			},
			'res': {
				'selector_json': '',
				'next_step': 'content'
			}
		},
		"content": {
			'type': 'db',
			'table_name': 'AnnualHealthStasticClassification',
			'unique': ['HealthPath'],
			'upsert': True,
			'fields': [{
				'name': 'HealthName',
				'selector_json': 'name',
				'required': True
			}, {
				'name': 'HealthPath',
				'selector_json': 'id',
				'required': True
			}],
			'res': [
			{
				'selector_json': 'isParent',
				'data_validator': lambda m,_: m == 'true',
				'data_postprocessor': lambda _,meta: meta['HealthPath'],
				'next_step': 'begin'
			},
			{
				'selector_json': 'id',
				'next_step': 'rows'
			} 
			]
		},
		"rows": {
			'req': {
				'method': 'post',
				'url': lambda _id, meta: 'http://data.stats.gov.cn/easyquery.htm?m=QueryData&dbcode=hgnd&rowcode=zb&colcode=sj&wds=%5B%5D&dfwds=' + urllib.quote('[{"wdcode":"zb","valuecode":"' + _id + '"},{"wdcode":"sj","valuecode":"LAST20"}]')
			},
			'res': {
				'data_preprocessor': get_code_mapping,
				'selector_json': 'returndata.datanodes',
				'next_step': 'db'
			},
		},
		"db": {
			'type': "db",
			'unique': ['HealthDataTypeID', 'StatisticType', 'DataYear'],
			'upsert': True,
			'table_name': "AnnualHealthStastic",
			'fields': [{
				'name': 'HealthName', 'value': None
			}, {
				'name': 'HealthPath', 'value': None
			}, {
				'name': 'HealthDataTypeID',
				'selector': lambda _,meta: meta['$$info_id']
			}, {
				'name': 'StatisticType',
				'selector_json': 'wds.0.valuecode',
				'data_postprocessor': lambda code, meta: meta['$$mapping_code_to_zb'][code]['cname'],
				'required': True
			}, {
				'name': 'StatisticUnit',
				'selector_json': 'wds.0.valuecode',
				'data_postprocessor': lambda code, meta: meta['$$mapping_code_to_zb'][code]['unit'],
				'required': True
			}, {
				'name': 'StatisticTypeComment',
				'selector_json': 'wds.0.valuecode',
				'data_postprocessor': lambda code, meta: meta['$$mapping_code_to_zb'][code]['memo']
			}, {
				'name': 'DataYear',
				'selector_json': 'wds.1.valuecode',
				'data_type': 'int',
				'required': True
			}, {
				'name': 'AffectedPopulation',
				'selector_json': 'data.data',
				'data_type': 'float'
			}]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

