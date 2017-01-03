#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig

class ScrapyConfig(ScrapyWrapperConfig):
	begin_urls = ["http://www.biomart.cn/supply/10030119.htm"]
	steps = {
		"begin": {
			'res': [{
				'selector_xpath': '//a/@href',
				'selector_regex': '(http://www.biomart.cn/infosupply/.*.htm)',
				'next_step': 'content'
			},
			{
				'selector_href_text': '>',
				'next_step': 'begin'
			}]
		},
		"content": {
			'res': {
				'selector_xpath': '//body',
				'next_step': 'content_parse'
			}
		},
		"content_parse": {
			'type': 'intermediate',
			'res': {
				'selector_css': '#j_tab3_ct',
				'next_step': 'db'
			},
			"fields": [{
				'name': 'ChineseName',
				'selector_css': 'div.product_attr h1',
				'selector_regex': '([^A-Za-z]*)'
			}, {
				'name': 'EnglishName',
				'selector_css': 'div.product_attr h1',
				'selector_regex': '[^A-Za-z]*(.*)'
			}, {
				'name': "CompanyName",
				'selector_css': 'li.m-pro-info-l a'
			}, {
				'name': 'ContactPerson',
				'selector_css': 'dl.par_top',
				'selector_regex': '联系人：([^<]*)',
				'required': True
			}, {
				'name': 'TelephoneNumber',
				'selector_css': 'dl.par_top',
				'selector_regex': '电话：([^<]*)'
			}, {
				'name': 'EmailAddress',
				'selector_css': 'dl.par_top',
				'selector_regex': '邮件：([^<]*)'
			}, {
				'name': 'CellphoneNumber',
				'selector_css': 'dl.par_top',
				'selector_regex': '手机：([^<]*)'
			}, {
				'name': 'CurrentAddress',
				'selector_css': 'dl.par_top',
				'selector_regex': '地址：([^<]*)'
			}, {
				'name': 'MerchantCredibilityScore',
				'selector_xpath': '//dd[@class="star"]/a/span/@class',
				'data_type': 'int'
			}, {
				'selector_xpath': '//*[@id="j_product_info"]/ul/li[3]/text()',
				'name': 'PlaceOfOrigin',
			}]
		},
		"db": {
			'type': "db",
			'table_name': "ExtractInfo",
			'fields': [{
				'name': "DetailedInfo",
				'selector_css': '#_info_desc',
				'strip_tags': False,
				'required': True
			}, {
				'selector_table_sibling': u'品牌：',
				'name': 'BrandName',
			}, {
				'selector_table_sibling': u'货号：',
				'name': 'ProductID'
			}, {
				'selector_table_sibling': u'供应商：',
				'name': 'SupplierName'
			}, {
				'selector_table_sibling': u'CAS号：',
				'name': 'CasID'
			}, {
				'selector_table_sibling': u'保质期：',
				'name': 'ShelfLife'
			}, {
				'selector_table_sibling': u'数量：',
				'name': 'InventoryLevel'
			}, {
				'selector_table_sibling': u'规格：',
				'name': 'Specification'
			}, {
				'name': 'PlaceOfOriginID',
				'reference': {
					'field': 'PlaceOfOrigin',
					'table': 'TB_Addresses',
					'remote_field': 'Name',
					'remote_id_field': 'PID',
					'match': 'lpm'
				}
			}]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

