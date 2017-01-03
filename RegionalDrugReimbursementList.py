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
			'res': {
				'selector_xpath': '//a/@href',
				'selector_regex': '(/yibaomulu/.*\.htm)',
				'next_step': 'content'
			}
		},
		"content": {
			'res': {
				'next_step': 'rows',
			},
		},
		"rows": {
			'type': 'intermediate',
			'fields': [{
				'name': "RegionID",
				'reference': {
					'field': "Region",
					'table': "TB_Addresses",
					'remote_field': "Name",
					'remote_id_field': "PID",
					'match': 'lpm'
				}
			}, {
				'name': 'Region',
				'selector_css': '#yibaomulu-content h1',
				'selector_regex': '# (.{3})',
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
			'fields': [{
				'name': "DrugClassification",
				'selector_xpath': '//td[1]',
				'selector': lambda n,meta: get_classification(n, meta)
			}, {
				'name': "DrugName",
				'selector_xpath': '//td[3]',
				'required': True
			}, {
				'name': "DrugNameEnglish",
				'selector_xpath': '//td[4]'
			}, {
				'name': "DosageType",
				'selector_xpath': '//td[5]'
			}, {
				'name': "Classification",
				'selector_xpath': '//td[1]'
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

