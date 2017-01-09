#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig


class ScrapyConfig(ScrapyWrapperConfig):
	begin_urls = ["http://www.phsciencedata.cn/Share/ky_sjml.jsp?id=8defcfc2-b9a4-4225-b92c-ebb002321cea&show=0"]
	steps = {
		"begin": {
			'req': { 'webview': True },
			'res': [{
				'selector_css': 'div.biao',
				'next_step': 'db_major_class'
			},
			{
				'selector_css': 'div.con > p > a',
				'next_step': 'db_class'
			}]
		},
		"db_major_class": {
			'type': "db",
			'table_name': "DiseaseClassification",
			'fields': [{
				'name': 'DiseaseName',
				'selector_xpath': '//h4/text()',
				'required': True
			}, {
				'name': 'DiseasePath',
				'selector_xpath': '/div/@id',
				'required': True
			}]
		},
		"db_class": {
			'type': "db",
			'table_name': "DiseaseClassification",
			'fields': [{
				'name': 'DiseaseName',
				'selector_xpath': '//a',
				'required': True
			}, {
				'name': 'DiseasePath',
				'selector_xpath': '//a/@itemid',
				'required': True
			}],
			'res': {
				'selector_xpath': '//a/@href',
				'selector_regex': '(ky_sjml.jsp\?id=.*)',
				'next_step': 'content'
			}
		},
		"content": {
			'req': { 'webview': True },
			'res': {
				'selector_css': '.content_r',
				'next_step': 'db'
			}
		},
		"db": {
			'type': "db",
			'table_name': "DiseaseInfo",
			'fields': [{
				'name': "DiseaseID",
				'selector': lambda _, meta: meta['$$info_id'],
				'required': True
			}, {
				'name': "DiseaseDescription",
				'selector_css': '#tabs-note',
				'required': True,
				'strip_tags': False
			}, {
				'name': "DiseaseName",
				'value': None
			}, {
				'name': "DiseasePath",
				'value': None
			}]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

