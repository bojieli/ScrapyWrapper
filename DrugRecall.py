#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
from scrapy.selector import Selector

def parse_DrugName_Filter(str_temp):
    find_flag=0
    if str_temp.find(u'关于')>=0:
        find_flag = str_temp.find(u'关于')
        str_temp=str_temp[find_flag+2:]
        if str_temp.find(u'做好') >= 0:
            find_flag = str_temp.find(u'做好')
            str_temp = str_temp[find_flag+2:]
        if str_temp.find(u'查处') >= 0:
            find_flag = str_temp.find(u'查处')
            str_temp = str_temp[find_flag+2:]
        print '-----------', str_temp
    elif str_temp.find(u'责令')>=0:
        find_flag = str_temp.find(u'责令')
        str_temp=str_temp[find_flag+2:]
        print '-----------', str_temp
    elif str_temp.find(u'通告')>=0:
        find_flag = str_temp.find(u'通告')
        str_temp = str_temp[find_flag + 2:]
        print '-----------', str_temp
    else:
        pass
    return str_temp

def parse_CompanyName(meta):
	if 'CompanyName' in meta and meta['CompanyName']:
		temp_CompanyName = meta['CompanyName']
		s_temp = parse_DrugName_Filter(temp_CompanyName)
		print u'整理：：：：', s_temp
		if s_temp.find(u'和') >= 0:
			oldlen = len(s_temp)
			newlen = len(s_temp.replace(u'公司', u''))
			if oldlen == newlen + 4:
				lists = []
				lists = s_temp.split(u'和')
				print lists[0], lists[1]
				meta['$$flag_List'] = lists
				meta['$$flag_resource'] = 'DrugRecall'
			else:
				meta['CompanyName'] = s_temp
				meta['$$reference_postprocessor'] = True
		else:
			meta['CompanyName']=s_temp
			meta['$$reference_postprocessor'] = True
	return meta

class ScrapyConfig(ScrapyWrapperConfig):
	begin_urls = ["http://www.sda.gov.cn/WS01/CL1058/"]
	steps = {
		"begin": {
			'res': [{
				'selector_xpath': '//a/@href',
				'selector_regex': '(\.\./CL[0-9]*/.*\.html)',
				'next_step': 'content'
			},
			{
				'selector_href_text_contains': u'下一页',
				'next_step': 'begin'
			}]
		},
		"content": {
			'res': {
				'selector_xpath': '/html/body/table[2]/tbody/tr/td/table',
				'keep_html_tags': True,
				'next_step': 'db'
			}
		},
		"db": {
			'type': "db",
			'table_name': "DrugRecall",
			'unique': ['PublicationDate', 'Headline'],
			'postprocessor': parse_CompanyName,
			'upsert': True,
			'fields': [{
				'name': "DrugManufacturerID",
				'reference': {
					'field': "CompanyName",
					'table': "TB_Resources_MedicineProductionUnit",
					'remote_field': "CompanyName",
					'remote_id_field': "ResID"
				}
			}, {
				'name': "PublicationDate",
				'selector_css': 'td.articletddate3',
				'selector_regex': u'([0-9]*年[0-9]*月[0-9]*日)',
				'data_type': "Date",
				'required': True
			}, {
				'name': "Headline",
				'selector_css': 'td.articletitle3',
				'required': True
			}, {
				'name': "CompanyName",
				'selector_css': 'td.articletitle3',
				'selector_regex': u'(.*公司)',
			}, {
				'name': "DrugName",
				'selector_css': 'td.articletitle3',
				'selector_regex': u'召回(.*)',
			}, {
				'name': "DetailContent",
				'selector_css': 'td.articlecontent3',
				'strip_tags': False,
				'download_images': True
			},{
				'name': "$$tempList",
				'strip_tags': False,
				'selector_xpath': '//*/tr/td/table'
			}
			]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

