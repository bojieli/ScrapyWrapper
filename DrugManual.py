#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig

class ScrapyConfig(ScrapyWrapperConfig):
	crawlera_enabled = True

	def url_generator(self):
		for i in range(60000,0,-1):
			yield 'http://db.yaozh.com/instruct/' + str(i) + '.html'


	begin_urls = url_generator

	steps = {
		"begin": {
			'res': {
				'next_step': 'db'
			}
		},
		"db": {
			'type': "db",
			'table_name': "DrugManual",
			'unique': ['DrugName', 'SourceOfManual'],
			'upsert': True,
			'fields': [
			{
				'name': "DrugID",
				'reference': {
					'table': "TB_Resources_MedicineMadeInChina",
					'fields': ["DrugName"],
					'remote_fields': ["CnName"],
					'remote_id_field': 'ResID'
				}
			}, {
				'name': "DrugName",
				'selector_regex': "通\s*用\s*名\s*：(.*?)<br>",
				'required': True
			}, {
				'name': "SourceOfManual",
				'selector_regex': "说明书来源:</span>(.*?)</div>",
				'required': True
			}, {
				'name': "Composition",
				'selector_regex': "<b>【成分】</b>(.*?)</p>"
			}, {
				'name': "Characteristics",
				'selector_regex': "<b>【性状】</b>(.*?)</p>"
			}, {
				'name': "Indication",
				'selector_regex': "<b>【功能主治】</b>(.*?)</p>"
			}, {
				'name': "UsageAndDosage",
				'selector_regex': "<b>【用法用量】</b>(.*?)</p>"
			}, {
				'name': "SideEffects",
				'selector_regex': "<b>【不良反应】</b>(.*?)</p>"
			}, {
				'name': "Warnings",
				'selector_regex': "<b>【禁忌】</b>(.*?)</p>"
			}, {
				'name': "KeyMatters",
				'selector_regex': "<b>【注意事项】</b>(.*?)</p>"
			}, {
				'name': "PregnancyAndBreastFeedingWarnings",
				'selector_regex': "<b>【孕妇及哺乳期妇女用药】</b>(.*?)</p>"
			}, {
				'name': "ChildrenWarnings",
				'selector_regex': "<b>【儿童用药】</b>(.*?)</p>"
			}, {
				'name': "ElderlyWarnings",
				'selector_regex': "<b>【老年患者用药】</b>(.*?)</p>"
			}, {
				'name': "DrugInteractions",
				'selector_regex': "<b>【药物相互作用】</b>(.*?)</p>"
			}, {
				'name': "DrugOverdose",
				'selector_regex': "<b>【药物过量】</b>(.*?)</p>"
			}, {
				'name': "PharmacologyAndToxicology",
				'selector_regex': "<b>【药理毒理】</b>(.*?)</p>"
			}, {
				'name': "pharmacokinetics",
				'selector_regex': "<b>【药代动力学】</b>(.*?)</p>"
			}, {
				'name': "DrugStorage",
				'selector_regex': "<b>【贮藏】</b>(.*?)</p>"
			}, {
				'name': "DrugPackaging",
				'selector_regex': "<b>【包装】</b>(.*?)</p>"
			}, {
				'name': "ShelfLife",
				'selector_regex': "<b>【有效期】</b>(.*?)</p>"
			}, {
				'name': "ProductStandard",
				'selector_regex': "<b>【执行标准】</b>(.*?)</p>"
			}, {
				'name': "ApprovalNumber",
				'selector_regex': "<b>【批准文号】</b>(.*?)</p>"
			}, {
				'name': "Manufacturer",
				'selector_regex': "<b>【生产名称】</b>(.*?)</p>"
			}, {
				'name': "Specification",
				'selector_regex': "<b>【规格】</b>(.*?)</p>"
			}
			]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

