#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig

class ScrapyConfig(ScrapyWrapperConfig):
	def url_generator(self):
		for i in range(16913,0,-1):
			#yield 'http://db.yaozh.com/api/index.php/Home/index/yaopinjiage/id/' + str(i)
			yield 'http://127.0.0.1:9576/instruct/id/' + str(i)


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
			'table_name': "DrugManual",
			'unique': ['DrugName', 'Manufacturer'],
			'upsert': True,
			'fields': [
			{
				'name': "DrugID",
				'reference': {
					'table': "TB_Resources_MedicineMadeInChina",
					'fields': ["DrugName", "Manufacturer"],
					'remote_fields': ["CnName", "ProductionUnit"],
					'remote_id_field': 'ResID'
				}
			}, {
				'name': "DrugName",
				'selector_json': "me_name",
				'required': True
			}, {
				'name': "SourceOfManual",
				'selector_json': "me_source"
			}, {
				'name': "Composition",
				'selector_json': "me_chengfen"
			}, {
				'name': "Characteristics",
				'selector_json': "me_xingzhuang"
			}, {
				'name': "Indication",
				'selector_json': "me_zhuzhi"
			}, {
				'name': "UsageAndDosage",
				'selector_json': "me_yongfa"
			}, {
				'name': "SideEffects",
				'selector_json': "me_fanying"
			}, {
				'name': "Warnings",
				'selector_json': "me_jingji"
			}, {
				'name': "KeyMatters",
				'selector_json': "me_zhuyi",
			}, {
				'name': "PregnancyAndBreastFeedingWarnings",
				'selector_json': "me_yunfu"
			}, {
				'name': "ChildrenWarnings",
				'selector_json': "me_ertong"
			}, {
				'name': "ElderlyWarnings",
				'selector_json': "me_laonian"
			}, {
				'name': "DrugInteractions",
				'selector_json': "me_xianghuzhuoyong"
			}, {
				'name': "DrugOverdose",
				'selector_json': "me_guoliang"
			}, {
				'name': "PharmacologyAndToxicology",
				'selector_json': "me_yaolidaoli"
			}, {
				'name': "pharmacokinetics",
				'selector_json': "me_yaodai"
			}, {
				'name': "DrugStorage",
				'selector_json': "me_zhucang"
			}, {
				'name': "DrugPackaging",
				'selector_json': "me_baozhuang"
			}, {
				'name': "ShelfLife",
				'selector_json': "me_yaoxiaoqi"
			}, {
				'name': "ProductStandard",
				'selector_json': "me_zhixingbiaozhun"
			}, {
				'name': "ApprovalNumber",
				'selector_json': "me_pizhunwenhao"
			}, {
				'name': "Manufacturer",
				'selector_json': "me_changjia"
			}, {
				'name': "Specification",
				'selector_json': "me_guige"
			}
			]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

