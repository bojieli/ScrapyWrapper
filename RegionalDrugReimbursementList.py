#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
import re

last_classification = None
def get_classification(name, meta):
	global last_classification
	m = re.search('^([0-9][0-9]*.)*([0-9][0-9]*) ([^ ]*)$', name)
	if m:
		last_classification = m.group(3)
		return m.group(3)
	else:
		return last_classification

class ScrapyConfig(ScrapyWrapperConfig):
	begin_urls = ["http://www.yaopinnet.com/tools/yibao.asp"]
	steps = {
		"begin": {
			'res': [{
				'selector_href_text': u'中药部分',
				'next_step': 'content_traditional'
			}, {
				'selector_href_text': u'西药部分',
				'next_step': 'content_non_traditional'
            }]
		},
		"content_traditional": {
            'fields': [{'name': 'IsTraditionalMedicine', 'value': 1}],
			'res': {
				'next_step': 'rows',
			},
		},
		"content_non_traditional": {
            'fields': [{'name': 'IsTraditionalMedicine', 'value': 0}],
			'res': {
				'next_step': 'rows',
			},
		},
		"rows": {
			'type': 'intermediate',
			'fields': [{
				'name': "RegionID",
				'reference': { 'field': "Region", 'match': 'address' }
			}, {
				'name': 'Region',
				'selector_css': '#yibaomulu-content h1',
				'selector_regex': '(.{3})',
				'required': True
			}],
			'res': {
				'selector_css': '#yibaomulu-content table tr',
				'next_step': 'db'
			},
		},
		"db": {
			'type': "db",
			'table_name': "RegionalDrugReimbursementList",
			'unique': ['SerialNumber', 'DrugName', 'Region', 'DosageType'],
			'upsert': True,
			'fields': [{
				'name': "DrugClassification",
				'selector_xpath': '//td[1]',
				'selector': lambda n,meta: get_classification(n, meta)
			}, {
				'name': "DrugName",
				'selector_xpath': '//td[3]',
				'required': True
            }, {
                'name': "DrugID",
                'reference': {
					'table': "TB_Resources_MedicineMadeInChina",
					'fields': ["DrugName"],
					'remote_fields': ["CnName"],
					'remote_id_field': 'ResID'
                }
			}, {
				'name': "DrugNameEnglish",
				'selector_xpath': '//td[4]'
			}, {
				'name': "DosageType",
				'selector_xpath': '//td[5]'
			}, {
				'name': "Classification",
				'selector_xpath': '//td[2]'
			}, {
				'name': "DrugClassificationID",
				'reference': {
					'field': 'DrugClassification',
					'table': 'DrugClassification',
					'remote_field': 'ClassificationName'
				}
			}, {
				'name': "Comment",
				'selector_xpath': '//td[6]'
			}, {
				'name': "AdjustmentInfo",
				'selector_xpath': '//td[7]'
			}, {
				'name': "SerialNumber",
				'selector_xpath': '//td[1]',
				'data_type': 'int',
				'required': True
			}]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

