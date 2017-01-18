#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig

class ScrapyConfig(ScrapyWrapperConfig):
	begin_urls = ["http://www.sda.gov.cn/WS01/CL1058/"]
	steps = {
		"begin": {
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
			'table_name': "DrugRecall",
			'unique': ['PublicationDate', 'Headline'],
			'upsert': True,
			'fields': [{
				'name': "DrugManufacturerID",
				'reference': {
					'field': "CompanyName",
					'table': "TB_Resources_MedicineProductionUnit",
					'remote_field': "CompanyName",
					'remote_id_field': "ResID"
				}
			}, {
				'name': "PublicationDate",
				'selector_css': 'td.articletddate3',
				'selector_regex': u'([0-9]*年[0-9]*月[0-9]*日)',
				'data_type': "Date",
				'required': True
			}, {
				'name': "Headline",
				'selector_css': 'td.articletitle3',
				'required': True
			}, {
				'name': "CompanyName",
				'selector_css': 'td.articletitle3',
				'selector_regex': u'(.*公司)',
			}, {
				'name': "DrugName",
				'selector_css': 'td.articletitle3',
				'selector_regex': u'召回(.*)',
			}, {
				'name': "DetailContent",
				'selector_css': 'td.articlecontent3',
				'strip_tags': False,
				'download_images': True
			}
			]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

