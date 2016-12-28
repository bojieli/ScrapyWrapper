#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig

class ScrapyConfig(ScrapyWrapperConfig):
	crawlera_enabled = True

	def url_generator(self):
		for i in range(1,100):
			#yield 'http://db.yaozh.com/api/index.php/Home/index/yaopinjiage/id/' + str(i)
			yield 'http://app1.sfda.gov.cn/datasearch/face3/content.jsp?tableId=119&tableName=TABLE119&tableView=%D0%E9%BC%D9%B9%E3%B8%E6%C6%F3%D2%B5%C3%FB%C2%BC&Id=' + str(i)

	begin_urls = url_generator
	#begin_urls = ["http://db.yaozh.com/api/index.php/Home/index/yaopinzhongbiao/id/3542343"]

	steps = {
		"begin": {
			'res': [{
				'selector_css': 'div.listmain',
				'next_step': 'db'
			}, {
                'selector_regex': '(&yunsuo_session_verify=[0-9A-Za-z]*)',
                'next_step': 'begin',
                'data_postprocessor': lambda verify_code, meta: meta['$$url'] + verify_code
            }]
		},
		"db": {
			'type': "db",
			'table_name': "InaccurateAdvertisement",
			'fields': [
			{
				'name': "DrugManufacturerID",
				'reference': {
					'table': "TB_Resources_MedicineProductionUnit",
					'field': "DrugManufacturerName",
					'remote_field': "CompanyName",
					'remote_id_field': 'ResID'
				}
			}, {
				'name': "ProductType",
				'selector_table_sibling': u'产品类别'
			}, {
				'name': "ProductNameInAd",
				'selector_table_sibling': u'广告中标识产品名称'
			}, {
				'name': "ProductName",
				'selector_table_sibling': u'产品名称',
				'required': True
			}, {
				'name': "DrugManufacturerName",
				'selector_table_sibling': u'生产企业名称'
			}, {
				'name': "DrugManufacturerLocation",
				'selector_table_sibling': u'生产企业所在地'
			}, {
				'name': "ProductApprovalNumber",
				'selector_table_sibling': u'产品批准文号'
			}, {
				'name': "DetailContent",
				'selector_table_sibling': u'违法内容简述'
			}, {
				'name': "CFDAAnnouncementNumber",
				'selector_table_sibling': u'总局通告号'
			}, {
				'name': "CFDAAnnouncementDate",
				'selector_table_sibling': u'总局通告时间',
				'data_type': 'Date',
				'required': True
			}
			]
		}
	}


myspider = SpiderFactory(ScrapyConfig(), __name__)
