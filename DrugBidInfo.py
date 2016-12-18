#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderWrapper
from scrapywrapper.config import ScrapyWrapperConfig

class ScrapyConfig(ScrapyWrapperConfig):
	def url_generator(self):
		for i in range(3500000,0,-1):
			yield 'http://db.yaozh.com/api/index.php/Home/index/yaopinzhongbiao/id/' + str(i)

	#begin_urls = self.url_generator
	begin_urls = ["http://db.yaozh.com/api/index.php/Home/index/yaopinzhongbiao/id/3542343"]
	steps = {
		"begin": {
			'req': {
				'method': "post",
				'post_rawdata': "access_token=5555f086252b2c47debad752b5272bb9&client=Android"
			},
			'res': {
				'next_step': 'db'
			}
		},
		"db": {
			'type': "db",
			'table_name': "DrugBidInfo",
			'fields': [
			{
				'name': "DrugID",
				'reference': {
					'table': "TB_Resources_MedicineMadeInChina",
					'fields': ["DrugGenericName", "DrugManufacturerName"],
					'remote_fields': ["CnName", "ProductionUnit"]
				}
			}, {
				'name': "DrugGenericName",
				'selector_json': "data.me_name"
			}, {
				'name': "DrugRetailName",
				'selector_json': "data.me_brandname"
			}, {
				'name': "DosageType",
				'selector_json': "data.me_jixing"
			}, {
				'name': "Specification",
				'selector_json': "data.me_guifanjixing"
			}, {
				'name': "PackagingRatio",
				'selector_json': "data.me_guige"
			}, {
				'name': "UnitOfMeasurement",
				'selector_json': "data.me_packaging"
			}, {
				'name': "BidPrice",
				'selector_json': "data.me_feiyong"
			}, {
				'name': "QualityLevel",
				'selector_json': "data.me_qlevel"
			}, {
				'name': "DrugManufacturerName",
				'selector_json': "data.me_shengchanqiye"
			}, {
				'name': "TenderCompany",
				'selector_json': "data.me_bidder"
			}, {
				'name': "BidProvince",
				'selector_json': "data.me_first"
			}, {
				'name': "BidProvinceID",
				'data_preprocessor': lambda province: province + u'省',
				'reference': {
					'table': "TB_Addresses",
					'field': "BidProvince",
					'remote_field': "Name"
				}
			}, {
				'name': "PublicationDate",
				'selector_json': "data.me_approvaldate"
			}, {
				'name': "CommentInfo",
				'selector_json': "data.me_remarks2"
			}, {
				'name': "SourceDocument",
				'selector_json': "data.me_source"
			}, {
				'name': "SourceDocumentUrl",
				'selector_json': "data.xq_source"
			}]
		}
	}

class Spider(SpiderWrapper):
	config = ScrapyConfig()

