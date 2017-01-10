#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
import datetime

class ScrapyConfig(ScrapyWrapperConfig):
	#crawlera_enabled = True

	def url_generator(self):
		for i in range(158900,600000):
			#yield 'http://db.yaozh.com/api/index.php/Home/index/yaopinjiage/id/' + str(i)
			yield 'http://ysk.99.com.cn/ys/' + str(i) + '.html'

	begin_urls = url_generator
	#begin_urls = ["http://db.yaozh.com/api/index.php/Home/index/yaopinzhongbiao/id/3542343"]

	steps = {
		"begin": {
			'res': [{
				'selector_css': '.s-infor-txt',
				'next_step': 'db'
            }]
		},
		"db": {
			'type': "db",
			'table_name': "DoctorRecord",
			'fields': [
			{
				'name': "DoctorName",
				'selector_dt': u'医生姓名：',
				'required': True
			}, {
				'name': "DoctorGender",
				'selector_dt': u'性',
				'required': True
			}, {
				'name': "DoctorLevel",
				'selector_dt': u'职'
			}, {
				'name': "PracticeType",
				'selector_dt': u'科'
			}, {
				'name': "PracticeLocation",
				'selector_dt': u'所属医院：',
				'required': True
			}, {
				'name': "PracticeCertificateNumber",
				'selector_dt': u'执业证书编码'
			}, {
				'name': "Speciality",
				'selector_dt': u'擅'
			}, {
				'name': "Introduction",
				'selector_dt': u'医生简介：'
			}, {
				'name': "DataEntryDate",
				'selector': lambda _,__: datetime.datetime.today().strftime('%Y-%m-%d'),
				'data_type': 'Date',
				'required': True
			}, {
				'name': "LocationID",
				'reference': {
					'field': 'PracticeLocation',
					'table': 'TB_Addresses',
					'remote_field': 'Name',
					'remote_id_field': 'PID',
					'match': 'lpm'
				}
			}
			]
		}
	}


myspider = SpiderFactory(ScrapyConfig(), __name__)
