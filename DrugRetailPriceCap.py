#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig

class ScrapyConfig(ScrapyWrapperConfig):
	def url_generator(self):
		for i in range(769999,0,-1):
			#yield 'http://db.yaozh.com/api/index.php/Home/index/yaopinjiage/id/' + str(i)
			yield 'http://128.199.95.148:9574/yaopinjiage/id/' + str(i)


	begin_urls = url_generator
	#begin_urls = ["http://db.yaozh.com/api/index.php/Home/index/yaopinzhongbiao/id/3542343"]
	steps = {
		"begin": {
			'req': {
				'method': "post",
				'post_formdata': {
					"access_token": "5555f086252b2c47debad752b5272bb9",
					"client": "Android"
				}
			},
			'res': {
				'next_step': 'db'
			}
		},
		"db": {
			'type': "db",
			'table_name': "DrugRetailPriceCap",
			'fields': [
			{
				'name': "DrugID",
				'reference': {
					'table': "TB_Resources_MedicineMadeInChina",
					'fields': ["DrugGenericName", "DrugManufacturerName"],
					'remote_fields': ["CnName", "ProductionUnit"],
					'remote_id_field': 'ResID'
				}
			}, {
				'name': "DrugName",
				'selector_json': "药品名称",
				'required': True
			}, {
				'name': "PriceSettingRegion",
				'selector_json': "定价地区"
			}, {
				'name': "DosageType",
				'selector_json': "剂型"
			}, {
				'name': "Specification",
				'selector_json': "规格"
			}, {
				'name': "UnitOfMeasurement",
				'selector_json': "单位"
			}, {
				'name': "RetailPriceCap",
				'selector_json': "最高零售价(元)"
			}, {
				'name': "DrugManufacturerName",
				'selector_json': "生产企业"
			}, {
				'name': "CommentInfo",
				'selector_json': "备注"
			}, {
				'name': "EffectiveDate",
				'selector_json': "执行日期",
			}, {
				'name': "RegionID",
				'reference': {
					'table': "TB_Addresses",
					'field': "PriceSettingRegion",
					'remote_field': "Name",
					'remote_id_field': 'PID',
					'match': 'prefix'
				}
			}, {
				'name': "DocumentNumber",
				'selector_json': "文件号"
			}]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

