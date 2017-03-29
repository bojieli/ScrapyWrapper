#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
import re

def get_year_month(url):
	year = ''
	month = ''
	params = url.split('?')[1].split('&')
	for param in params:
		key, value = param.split('=')
		if key == 'yearSel':
			year = value
		elif key == 'monthSel':
			if len(value) == 1:
				month = '0' + value
			else:
				month = value
	return year + month

class ScrapyConfig(ScrapyWrapperConfig):
	def begin_url_gen(self):
		baseurl = "http://chinacdc.cn:81/PF/page/runqian/runqianCondi.jsp?ID=custom&runqianId=17c6b12c-67d1-4ffe-84a0-934d84aaa93f&raqName=ReportZone.raq&reportType=1&zoneCode=%2000000000"
		for diseaseID in range(1, 200):
			disease_url = baseurl + '&diseaseId=' + str(diseaseID)
			for yearSel in range(2000, 2017):
				year_url = disease_url + '&yearSel=' + str(yearSel)
				yield year_url
				for monthSel in range(1, 13):
					month_url = year_url + '&monthSel=' + str(monthSel)
					yield month_url
	
	begin_urls = begin_url_gen

	steps = {
		"begin": {
			'res': [{
				'selector_css': '#report1',
				'next_step': 'row'
			}]
		},
		"row": {
			'type': "intermediate",
			'fields': [{
				'name': 'DiseaseID',
				'reference': {'table': 'DiseaseClassification', 'field': 'DiseaseName', 'remote_field': 'DiseaseName', 'remote_id_field': 'ID'},
				'required': True
			}, {
				'name': 'DiseaseName',
				'selector_xpath': '//td[@colspan=4]',
				# non-breakable space \xa0 produced by &nbsp;
				'data_postprocessor': lambda d,_: d.replace(' ','').replace(u'\xa0', u''),
				'required': True
			}, {
				'name': 'YearMonth',
				'selector': lambda _,meta: get_year_month(meta['$$url']),
				'required': True
			}],
			'res': [{
				'selector_xpath': '//tr[position()>2]',
				'next_step': 'db'
			}]
		},
		"db": {
			'type': "db",
			'table_name': "DiseaseAgeStatistic",
			'unique': ['DiseaseID', 'AgeGroup', 'YearMonth'],
			'upsert': True,
			'fields': [{
				'name': 'AgeGroup',
				'selector_xpath': '//td[1]',
				# non-breakable space \xa0 produced by &nbsp;
				'data_postprocessor': lambda d,_: d.replace(' ','').replace(u'\xa0', u''),
				'required': True
			}, {
				'name': 'AffectedPopulation',
				'selector_xpath': '//td[2]',
				'data_type': 'int'
			}, {
				'name': 'Deathtoll',
				'selector_xpath': '//td[3]',
				'data_type': 'int'
			}, {
				'name': 'Morbidity',
				'selector_xpath': '//td[4]',
				'data_type': 'float'
			}, {
				'name': 'Mortality',
				'selector_xpath': '//td[5]',
				'data_type': 'float'
			}],
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

