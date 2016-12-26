#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderWrapper
from scrapywrapper.config import ScrapyWrapperConfig

base_url = "http://www.sda.gov.cn/WS01/CL1851/"

class ScrapyConfig(ScrapyWrapperConfig):
	begin_urls = ["", "../CL1852/", "../CL1853/", "../CL1854/", "../CL1855/", "../CL1856/"]
	steps = {
		"begin": {
			'req': {
				'url': lambda url, meta: base_url + url
			},
			'res': [{
				'selector_xpath': '//a/@href',
				'selector_regex': '(\.\./CL[0-9]*/.*\.html)',
				'next_step': 'content'
			},
			{
				'selector_href_text_contains': u'下一页',
				'next_step': 'begin'
			}]
		},
		"content": {
			'req': {
				'url': lambda url, meta: base_url + url
			},
			'res': {
				'selector_xpath': '/html/body/table[2]/tbody/tr/td/table',
				'keep_html_tags': True,
				'next_step': 'db'
			}
		},
		"db": {
			'type': "db",
			'table_name': "DrugConsistencyEvaluation",
			'fields': [{
				'name': "PublicationDate",
				'selector_css': 'td.articletddate3',
				'selector_regex': '([0-9]*年[0-9]*月[0-9]*日)',
				'data_type': "Date",
				'required': True
			}, {
				'name': "Headline",
				'selector_css': 'td.articletitle3',
				'required': True
			}, {
				'name': "DetailContent",
				'selector_css': 'td.articlecontent3'
			}, {
				'name': "ClassificationNumber",
				'selector': lambda result, meta: meta['referer'][-2:-1] if meta['referer'][-2:-1].isdigit() else '0'
			}
			]
		}
	}

class Spider(SpiderWrapper):
	name = 'RandomInspection'
	config = ScrapyConfig()

