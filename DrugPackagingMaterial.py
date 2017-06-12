#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig

def parse_VarietyName_RegistrationNumber(meta):
    if 'VarietyName' in meta and meta['VarietyName']:
        temp_VarietyName=meta['VarietyName']
        if temp_VarietyName.find(u'药包字')>=0:
            meta['VarietyName']=meta['RegistrationNumber']
            meta['RegistrationNumber']=temp_VarietyName

    return meta

class ScrapyConfig(ScrapyWrapperConfig):
	use_http_proxy = True

	def url_generator(self):
		for i in range(10000,20000):
			#yield 'http://db.yaozh.com/api/index.php/Home/index/yaopinjiage/id/' + str(i)
			yield 'http://app1.sfda.gov.cn/datasearch/face3/content.jsp?tableId=6&tableName=TABLE6&tableView=%C5%FA%D7%BC%B5%C4%D2%A9%B0%FC%B2%C4&Id=' + str(i)

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
			'table_name': "DrugPackagingMaterial",
			'postprocessor': parse_VarietyName_RegistrationNumber,
			'unique': ['RegistrationNumber'],
			'upsert': True,
			'fields': [
			{
				'name': "VarietyName",
				'selector_table_sibling': u'品种名称',
				'required': True
			}, {
				'name': "RegistrationNumber",
				'selector_table_sibling': u'注册证号'
			}, {
				'name': "CompanyName",
				'selector_table_sibling': u'企业名称'
			}, {
				'name': "ProductSource",
				'selector_table_sibling': u'产品来源'
			}, {
				'name': "ApprovalDate",
				'selector_table_sibling': u'批准日期',
				'data_type': 'Date'
			}, {
				'name': "Specification",
				'selector_table_sibling': u'规格'
			}
			]
		}
	}


myspider = SpiderFactory(ScrapyConfig(), __name__)
