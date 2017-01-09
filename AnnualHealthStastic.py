#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
import re
import json
import demjson

def get_code_mapping(text, meta):
	obj = demjson.decode(text)
	mapping = {}
	for zb in obj['returndata']['wdnodes'][0]['nodes']:
		mapping[zb['code']] = zb['cname']
	meta['$$mapping_code_to_zb'] = mapping
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
			'fields': [{
				'name': 'HealthName',
				'selector_json': 'name',
				'required': True
			}, {
				'name': 'HealthPath',
				'selector_json': 'id',
				'required': True
			}],
			'res': [{
				'selector_json': 'id',
				'next_step': 'rows'
			}, {
				'selector_json': 'isParent',
				'data_validator': lambda m,_: m == 'True',
				'data_postprocessor': lambda _,meta: 'id=' + meta['HealthPath'] + '&dbcode=hgnd&wdcode=zb&m=getTree',
				'next_step': 'begin'
			}]
		},
		"rows": {
			'req': {
				'method': 'post',
				'url': lambda _id, meta: 'http://data.stats.gov.cn/easyquery.htm?m=QueryData&dbcode=hgnd&rowcode=zb&colcode=sj&wds=%5B%5D&dfwds=%5B%7B%22wdcode%22%3A%22zb%22%2C%22valuecode%22%3A' + _id + '%7D%5D&k1=1483425362507',
			},
			'res': {
				'data_preprocessor': get_code_mapping,
				'selector_json': 'returndata.datanodes',
				'next_step': 'db'
			},
		},
		"db": {
			'type': "db",
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
				'data_postprocessor': lambda code, meta: meta['$$mapping_code_to_zb'][code],
				'required': True
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

