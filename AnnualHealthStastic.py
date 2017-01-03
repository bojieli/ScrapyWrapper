#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
import re
import json

class ScrapyConfig(ScrapyWrapperConfig):
	begin_urls = ['http://data.stats.gov.cn/easyquery.htm']
	steps = {
		"begin": {
			'req': {
				'method': 'post',
				'post_formdata': 'id=A0O&dbcode=hgnd&wdcode=zb&m=getTree'
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
			'res': {
				'next_step': 'rows',
				'selector_json': 'id'
			},
		},
		"rows": {
			'req': {
				'method': 'post',
				'url': lambda url, meta: 'http://data.stats.gov.cn/easyquery.htm?m=QueryData&dbcode=hgnd&rowcode=zb&colcode=sj&wds=%5B%5D&dfwds=%5B%7B%22wdcode%22%3A%22zb%22%2C%22valuecode%22%3A' + url + '%7D%5D&k1=1483425362507',
			},
			'res': {
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
				'selector_json': 'wds.0.valuecode'
			}, {
				'name': 'DataYear',
				'selector_json': 'wds.1.valuecode',
				'data_type': 'int'
			}, {
				'name': 'AffectedPopulation',
				'selector_json': 'data.data',
				'data_type': 'float'
			}]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

