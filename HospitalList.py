#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig

class ScrapyConfig(ScrapyWrapperConfig):
	begin_urls = ["http://www.pharmnet.com.cn/search/template/yljg_index.htm"]
	steps = {
		"begin": {
			'res': {
				'selector_xpath': '//a/@href',
				'selector_regex': '(/search/index.cgi\?c1=.*&c2=.*&p=.*)',
				'next_step': 'list'
			}
		},
		'list': {
			"res": [{
				'selector_xpath': '//a/@href',
				'selector_regex': '(/search/detail.*)',
				'next_step': 'content'
			}, {
				'selector_href_text': ' >> ',
				'next_step': 'list'
			}]
		},
		"content": {
			'res': {
				'selector_xpath': '//body',
				'next_step': 'db'
			}
		},
		"db": {
			'type': "db",
			'table_name': "HospitalList",
			'fields': [{
				'name': "RegionID",
				'reference': {
					'field': "HospitalName",
					'table': "TB_Resources_MedicineProductionUnit",
					'remote_field': "CompanyName",
					'remote_id_field': "ResID",
					'match': 'lpm'
				}
			}, {
				'name': "HospitalName",
				'selector_table_sibling': u'医院名称：',
				'required': True
			}, {
				'selector_table_sibling': u'等　　级：',
				'name': 'HospitalLevel'
			}, {
				'selector_table_sibling': u'类　　型：	',
				'name': 'HospitalType'
			}, {
				'selector_table_sibling': u'是否医保定点：',
				'name': 'MedicalInsuranceLocation'
			}, {
				'selector_table_sibling': u'病 床 数：',
				'name': 'HospitalBed',
				'data_type': 'int'
			}, {
				'selector_table_sibling': u'门 诊 量：',
				'name': 'DailyVisit',
				'data_type': 'int'
			}, {
				'selector_table_sibling': u'地　　址：',
				'name': 'Address'
			}, {
				'selector_table_sibling': u'邮　　编：',
				'name': 'PostalCode'
			}, {
				'selector_table_sibling': u'联系电话：',
				'name': 'ContactTelephone'
			}, {
				'selector_table_sibling': u'网　　址：',
				'name': 'HospitalWebsite'
			}, {
				'selector_table_sibling': u'乘车路线：',
				'name': 'TravelRoute'
			}, {
				'selector_table_sibling': u'主要设备：',
				'name': 'MainEquipment'
			}, {
				'selector_table_sibling': u'特色专科：',
				'name': 'Specialty'
			}, {
				'selector_table_sibling': u'医院介绍：',
				'name': 'HospitalIntroduction'
			}
			]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)
