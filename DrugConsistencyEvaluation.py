#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
from urlparse import urljoin

base_url = "http://www.sda.gov.cn/WS01/"

class ScrapyConfig(ScrapyWrapperConfig):
	begin_urls = ["CL1851/", "CL1852/", "CL1853/", "CL1854/", "CL1855/", "CL1856/"]
	steps = {
		"begin": {
			'req': {
				'url': lambda url, meta: urljoin(base_url, url)
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
				'data_preprocessor': lambda result, meta: meta['referer'],
				'selector_regex': '.*CL([0-9]*)',
				'data_postprocessor': lambda n, meta: '1' if n == '1033' else '2' if n == '1842' or n == '1030' or n == '1031' else '3' if n == '1043' or n == '0885' or n ==     '0884' else '0'
			}
			]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

