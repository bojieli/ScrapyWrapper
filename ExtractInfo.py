#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
import re

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
				'data_postprocessor': lambda d,_: re.sub(r'[a-zA-Z0-9\s_-]*$', '', re.sub(r'^[a-zA-Z0-9\s]*', '', d))
			}, {
				'name': '$$Name',
				'selector_css': 'div.product_attr h1',
				'required': True
			}, {
				'name': 'EnglishName',
				'selector_xpath': u'//li[@title="英&nbsp;&nbsp;文&nbsp;&nbsp;名："]/text()',
				'selector': lambda x,meta: x if x else re.sub(r'[^a-zA-Z0-9\s_-]', '', meta['$$Name'])
			}, {
				'name': "CompanyName",
				'selector_css': 'li.m-pro-info-l a',
				'required': True
			}, {
				'name': 'ContactPerson',
				'selector_xpath': u'//dl[@class="par_top"]//span[text()="联系人："]/parent::p/text()',
			}, {
				'name': 'TelephoneNumber',
				'selector_xpath': u'//dl[@class="par_top"]//span[text()="电话："]/parent::p/text()',
			}, {
				'name': 'EmailAddress',
				'selector_xpath': u'//dl[@class="par_top"]//span[text()="邮件："]/parent::p/text()',
			}, {
				'name': 'CellphoneNumber',
				'selector_xpath': u'//dl[@class="par_top"]//span[text()="手机："]/parent::p/text()',
			}, {
				'name': 'CurrentAddress',
				'selector_xpath': u'//dl[@class="par_top"]//span[text()="地址："]/parent::p/text()',
			}, {
				'name': 'MerchantCredibilityScore',
				'selector_xpath': '//dd[@id="js_par_star"]/a/span/@class',
				'data_type': 'int'
			}, {
				'name': 'PlaceOfOrigin',
				'selector_xpath': u'//li[@title="产　　地："]/text()',
			}]
		},
		"db": {
			'type': "db",
			'table_name': "ExtractInfo",
			'unique': ['ChineseName', 'ProductID', 'CompanyName'],
			'upsert': True,
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
				'reference': { 'fields': ['PlaceOfOrigin', 'CurrentAddress', 'CompanyName'], 'match': 'address' }
			}]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

