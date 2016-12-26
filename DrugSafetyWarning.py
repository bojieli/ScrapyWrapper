#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderWrapper
from scrapywrapper.config import ScrapyWrapperConfig

base_url = "http://www.sda.gov.cn/WS01/CL1059/"

class ScrapyConfig(ScrapyWrapperConfig):
	begin_urls = [""]
	steps = {
		"begin": {
			'req': {
				'url': lambda url, meta: base_url + url
			},
			'res': [{
				'selector_xpath': '//a/@href',
				'selector_regex': '(\.\./CL0389/.*\.html)',
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
			'table_name': "DrugSafetyWarning",
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
				'name': "DrugName",
				'selector_table_sibling': u'药品名称'
			}, {
				'name': "DetailContent",
				'selector_css': 'td.articlecontent3'
			}, {
				'name': "ClassificationNumber",
				'selector_css': 'td.articletitle3',
				'data_postprocessor': lambda title: '1' if u'不良反应通报' in title else '2' if u'警戒快讯' in title else '3' if u'不良反应基本常识' in title else '4' if u'滥用检测基本常识' else '0'
			}
			]
		}
	}

class Spider(SpiderWrapper):
	name = 'RandomInspection'
	config = ScrapyConfig()
