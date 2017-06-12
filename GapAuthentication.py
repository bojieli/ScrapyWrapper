#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
from scrapy.selector import Selector

def parse_CompanyName(meta):
	if meta['CompanyName'] and meta['CompanyName']!=u'注册地址' and meta['CompanyName']!=u'存在的主要问题' and meta['CompanyName']!=u'生产地址':
		print '*****************************************',meta['CompanyName']
		return meta
	if '$$tempList' in meta and not meta['$$tempList']:
		if '$$tempList2' in meta and meta['$$tempList2']:
			meta['$$tempList']=meta['$$tempList2']

	if '$$tempList' in meta and meta['$$tempList']:
		content = meta['$$tempList']
		listtr=Selector(text=content, type="html").xpath('//tr').extract()
		se_flag=''
		CompanyNameList=[]
		tr_index=0
		for index, link in enumerate(listtr):
			lists = Selector(text=link, type="html").xpath('//td').extract()
			tr_index=index
			for index, links in enumerate(lists):
				aa=Selector(text=links).xpath('//span/text()').extract()
				if tr_index==0:
					if index == 0:
						se_flag = aa[0]
					pass
					print aa[0]
				else:
					if se_flag == u'企业名称':
						if index==0:
							print tr_index,u'企业名称','add',aa[0]
							CompanyNameList.append(aa[0])
						else:
							print tr_index,u'企业名称','view', aa[0]
					elif se_flag == u'序号':
						if index==2:

							print tr_index,u'序号','add', aa[0]
							CompanyNameList.append(aa[0])

						else:
							print tr_index,u'序号','view',index, aa[0]
		meta['$$flag_List']=CompanyNameList
		meta['$$flag_resource'] = 'GapAuthentication'
	return meta

class ScrapyConfig(ScrapyWrapperConfig):
	begin_urls = ["http://www.sda.gov.cn/WS01/CL1045/"]
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
				'next_step': 'db'
			}
		},
		"db": {
			'type': "db",
			'table_name': "GapAuthentication",
			'unique': ['PublicationDate', 'Headline'],
			'upsert': True,
			'fields': [{
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
				'selector_regex': u'企业名称：([^<]*)<br'
			}, {
				'name': "OrganizationNumer",
				'selector_regex': u'组织机构代码：([^<]*)<br'
			}, {
				'name': "CorporateRep",
				'selector_regex': u'法定代表人：([^<]*)<br'
			}, {
				'name': "QualityManInCharge",
				'selector_regex': u'质量负责人：([^<]*)<br'
			}, {
				'name': "RegistrationAddress",
				'selector_regex': u'注册地址：([^<]*)<br'
			}, {
				'name': "AddressID",
				'reference': { 'field': 'RegistrationAddress', 'match': 'address' }
			}, {
				'name': "PlantationType",
				'selector_regex': u'种植品种：([^<]*)<br'
			}, {
				'name': "PlantationRegion",
				'selector_regex': u'种植区域：([^<]*)<br'
			}, {
				'name': "InspectorName",
				'selector_regex': u'现场检查员：([^<]*)<br'
			}, {
				'name': "CFDACorporateRep",
				'selector_regex': u'国家食品药品监督管理总局食品药品审核查验中心法定代表人：([^<]*)<br'
			}, {
				'name': "EffectiveUntil",
				'selector_regex': u'有效期至：([^<]*)<',
				'data_type': 'Date'
			}, {
				'name': "DetailContent",
				'selector_css': 'td.articlecontent3',
				'strip_tags': False,
				'download_images': True
			},{
				'name': "$$tempList",
				'strip_tags': False,
				'selector_xpath': '//*/tr/td/table'
			},{
				'name': "$$tempList2",
				'strip_tags': False,
				'selector_xpath': '//*/tr/td/p/span/table'
			}
			]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

