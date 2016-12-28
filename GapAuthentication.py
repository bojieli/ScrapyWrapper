#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig


class ScrapyConfig(ScrapyWrapperConfig):
	begin_urls = ["http://www.sda.gov.cn/WS01/CL1045/"]
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
			'table_name': "GapAuthentication",
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
				'name': "CompanyName",
				'selector_regex': u'企业名称：(.*)<br'
			}, {
				'name': "OrganizationNumer",
				'selector_regex': u'组织机构代码：(.*)<br'
			}, {
				'name': "CorporateRep",
				'selector_regex': u'法定代表人：(.*)<br'
			}, {
				'name': "QualityManInCharge",
				'selector_regex': u'质量负责人：(.*)<br'
			}, {
				'name': "RegistrationAddress",
				'selector_regex': u'注册地址：(.*)<br'
			}, {
				'name': "AddressID",
				'reference': {
					'field': 'RegistrationAddress',
					'table': 'TB_Addresses',
					'remote_field': 'Name',
					'remote_id_field': 'PID',
					'match': 'lpm'
				}
			}, {
				'name': "PlantationType",
				'selector_regex': u'种植品种：(.*)<br'
			}, {
				'name': "PlantationRegion",
				'selector_regex': u'种植区域：(.*)<br'
			}, {
				'name': "InspectorName",
				'selector_regex': u'现场检查员：(.*)<br'
			}, {
				'name': "CFDACorporateRep",
				'selector_regex': u'国家食品药品监督管理总局食品药品审核查验中心法定代表人：(.*)<br'
			}, {
				'name': "EffectiveUntil",
				'selector_regex': u'有效期至：(.*)<br',
				'data_type': 'Date'
			}, {
				'name': "DetailContent",
				'selector_css': 'td.articlecontent3'
			}
			]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

