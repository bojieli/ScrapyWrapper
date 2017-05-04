#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig

def get_next_url(url):
	pattern = "xxgkml_1_4443"
	pos = url.find(pattern) + len(pattern)
	prefix = url[:pos]
	suffix = url[pos:]
	if suffix == '.htm':
		return prefix + '_1.htm'
	else:
		pagenum = int(suffix[1:-4]) + 1
		return prefix + '_' + str(pagenum) + '.htm'

class ScrapyConfig(ScrapyWrapperConfig):
	begin_urls = ["http://www.aqsiq.gov.cn/xxgk_13386/tsxx/yqts/xxgkml_1_4443.htm"]
	steps = {
		"begin": {
            'req': {'debug': True},
			'res': [{
				'selector_regex': 'href="(\./[^"]*)"',
				'next_step': 'content',
                'debug': True
			},
			{
				'selector_regex': u'(下一页)',
				'data_postprocessor': lambda _, meta: get_next_url(meta['$$url']),
				'next_step': 'begin',
                'debug': True
			}]
		},
		"content": {
            'req': {'debug': True},
			'res': {
				'selector_css': 'div.yy',
				'next_step': 'db',
                'debug': True
			}
		},
		"db": {
			'type': "db",
			'table_name': "DiseaseForecast",
			'unique': ['PublicationDate', 'Headline'],
			'upsert': True,
            'debug': True,
			'fields': [{
				'name': "PublicationDate",
				'selector_regex': u'发布时间：([0-9-]*)',
				'data_type': "Date",
				'required': True,
                'debug': True
			}, {
				'name': "Headline",
				'selector_css': 'h1',
				'required': True,
                'debug': True
			}, {
				'name': "DetailContent",
				'selector_css': 'div.TRS_Editor',
				'required': True,
				'strip_tags': False,
                'debug': True
			}]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

