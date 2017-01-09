#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
import re

def get_ordering(_, meta):
	if '$$order' in meta:
		meta['$$order'] += 1
		return str(meta['$$order'])
	else:
		meta['$$order'] = 1
		return str(1)

def remove_useless(_, meta):
	try:
		del meta['PublicationDate']
	except:
		pass
	try:
		del meta['Headline']
	except:
		pass
	try:
		del meta['DetailContent']
	except:
		pass

class ScrapyConfig(ScrapyWrapperConfig):
	def url_generator(self):
		prefix = "http://www.nhfpc.gov.cn/zhuzhan/yqxx/lists"
		suffix = ".shtml"
		yield prefix + suffix
		for i in range(2, 50):
			yield prefix + "_" + str(i) + suffix

	begin_urls = url_generator

	steps = {
		"begin": {
			'res': {
				'selector_xpath': '//div[@class = "contents"]//a/@href',
				'next_step': 'content'
			}
		},
		"content": {
			'res': {
				'selector_css': '#page_content',
				'next_step': 'db'
			}
		},
		"db": {
			'type': "db",
			'table_name': "InfectiousDiseaseInfo",
			'fields': [{
				'name': "PublicationDate",
				'selector_css': 'div.content_subtitle',
				'selector_regex': u'([0-9]{4}-[0-9]{2}-[0-9]{2})',
				'required': True
			}, {
				'name': "Headline",
				'selector_css': '#zoomtitle',
				'required': True
			}, {
				'name': "DetailContent",
				'selector_css': '#zoomcon',
				'strip_tags': False,
				'download_images': True
			}],
			'res': {
				'selector_css': "#zoomcon table tr",
				'next_step': 'db_subtable'
			}
		},
		"db_subtable": {
			'type': "db",
			'table_name': 'InfectiousDiseaseStatistic',
			'fields': [{
				'name': 'DiseaseID',
				'selector': lambda _,meta: meta['$$info_id'],
				'required': True
			}, {
				'name': 'DiseaseName',
				'selector_xpath': '//td[1]',
				'data_validator': lambda d, meta: "*" not in d,
				'data_postprocessor': lambda d, meta: d.replace(' ', '').replace(u'　', ''),
				'required': True
			}, {
				'name': 'AffectedPopulation',
				'selector_xpath': '//td[2]',
				'data_type': 'int'
			}, {
				'name': 'Deathtoll',
				'selector_xpath': '//td[3]',
				'data_type': 'int'
			}, {
				'name': 'SOrder',
				'selector': get_ordering,
				'required': True
			}, {
				'name': '$$remove_useless',
				'selector': remove_useless,
			}]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

