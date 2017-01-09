#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig

class ScrapyConfig(ScrapyWrapperConfig):
	crawlera_enabled = True

	def url_generator(self):
		for i in range(1,300000):
			#yield 'http://db.yaozh.com/api/index.php/Home/index/yaopinjiage/id/' + str(i)
			yield 'http://app1.sfda.gov.cn/datasearch/face3/content.jsp?tableId=70&tableName=TABLE70&tableView=%E6%89%A7%E4%B8%9A%E8%8D%AF%E5%B8%88%E8%B5%84%E6%A0%BC%E4%BA%BA%E5%91%98%E5%90%8D%E5%8D%95&Id=' + str(i)

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
			'table_name': "PharmacistRecord",
			'fields': [
			{
				'name': "PharmacistName",
				'selector_table_sibling': u'姓名',
				'required': True
			}, {
				'name': "PharmacistGender",
				'selector_table_sibling': u'性别'
			}, {
				'name': "ResidingProvince",
				'selector_table_sibling': u'所在省份'
			}, {
				'name': "ProvinceID",
				'reference': {
					'field': 'ResidingProvince',
					'table': 'TB_Addresses',
					'remote_field': 'Name',
					'remote_id_field': 'PID'
				}
			}, {
				'name': "CertificateNumber",
				'selector_table_sibling': u'资格证号'
			}, {
				'name': "WorkLocation",
				'selector_table_sibling': u'工作单位'
			}, {
				'name': "WorkType",
				'selector_table_sibling': u'类别'
			}, {
				'name': "CertificationYear",
				'selector_table_sibling': u'考试合格年度'
			}
			]
		}
	}


myspider = SpiderFactory(ScrapyConfig(), __name__)
