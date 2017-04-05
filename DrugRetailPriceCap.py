#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig

class ScrapyConfig(ScrapyWrapperConfig):
	def url_generator(self):
		for i in range(770000,1,-1):
			yield 'https://db.yaozh.com/yaopinjiage/' + str(i) + '.html'

	crawlera_enabled = True

	begin_urls = url_generator
	steps = {
		"begin": {
			'res': {
				'selector_css': 'div.body',
				'next_step': 'db',
				'required': True
			}
		},
		"db": {
			'type': "db",
			'table_name': "DrugRetailPriceCap",
			'unique': ['SourceID'],
			'upsert': True,
			'fields': [
			{
				'name': "$$DrugID_exact",
				'reference': {
					'table': "TB_Resources_MedicineMadeInChina",
					'fields': ["DrugName", "DrugManufacturerName"],
					'remote_fields': ["CnName", "ProductionUnit"],
					'remote_id_field': 'ResID'
				}
			}, {
				'name': "$$DrugID_name_only",
				'reference': {
					'table': "TB_Resources_MedicineMadeInChina",
					'fields': ["DrugName"],
					'remote_fields': ["CnName"],
					'remote_id_field': 'ResID'
				}
			}, {
				'name': "DrugID",
				'dependencies': ['$$DrugID_exact', '$$DrugID_name_only'],
				'selector': lambda _,meta: meta['$$DrugID_exact'] if meta['$$DrugID_exact'] else meta['$$DrugID_name_only'],
			}, {
				'name': "DrugName",
				'selector_table_sibling': u"药品名称",
				'required': True
			}, {
				'name': "PriceSettingRegion",
				'selector_table_sibling': u"定价地区"
			}, {
				'name': "DosageType",
				'selector_table_sibling': u"剂型"
			}, {
				'name': "Specification",
				'selector_table_sibling': u"规格"
			}, {
				'name': "UnitOfMeasurement",
				'selector_table_sibling': u"单位"
			}, {
				'name': "RetailPriceCap",
				'selector_table_sibling': u"最高零售价(元)",
				'data_type': 'float'
			}, {
				'name': "DrugManufacturerName",
				'selector_table_sibling': u"生产企业"
			}, {
				'name': "CommentInfo",
				'selector_table_sibling': u"备注"
			}, {
				'name': "EffectiveDate",
				'selector_table_sibling': u"执行日期",
				'data_type': 'Date',
				'required': True
			}, {
				'name': "RegionID",
				'reference': {
					'table': "TB_Addresses",
					'field': "PriceSettingRegion",
					'remote_field': "Name",
					'remote_id_field': 'PID',
					'match': 'lpm'
				}
			}, {
				'name': "DocumentNumber",
				'selector_table_sibling': u"文件号",
				'required': True
			}, {
				'name': 'SourceID',
				'data_preprocessor': lambda _,meta: meta['$$url'],
				'selector_regex': '([0-9]*)\.html',
				'data_type': 'int',
				'required': True
			}]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

