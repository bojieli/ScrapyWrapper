#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
from scrapy.selector import Selector

def parse_CompanyName(meta):
	if meta['CompanyName'] and meta['CompanyName']!=u'地址' and meta['CompanyName']!=u'存在的主要问题' and meta['CompanyName']!=u'生产地址':
		print '*****************************************',meta['CompanyName']
		return meta

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
							meta['ProductionAddress'] =''
							meta['DrugProductionPermitNumber']=''
							meta['Inspector'] = ''
						# elif index==3:
						#	meta['ProductionAddress']=aa[0]
						# elif index==4:
						#	meta['DrugProductionPermitNumber']=aa[0]
						# elif index==6:
						#	meta['Inspector']=aa[0]
						else:
							print tr_index,u'序号','view',index, aa[0]
		meta['$$flag_List']=CompanyNameList
		meta['$$flag_resource'] = 'RandomInspection'
	return meta

class ScrapyConfig(ScrapyWrapperConfig):
	begin_urls = ["http://www.sda.gov.cn/WS01/CL1850/"]
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
			'table_name': "RandomInspection",
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
				'name': "DetailContent",
				'selector_css': 'td.articlecontent3',
				'strip_tags': False,
				'download_images': True
			}, {
				'name': "CompanyName",
				'selector_table_sibling': u'企业名称',
			}, {
				'name': "CorporateRep",
				'selector_table_sibling': u'企业法定代表人'
			}, {
				'name': "DrugProductionPermitNumber",
				'selector_table_sibling': u'药品生产许可证编号'
			}, {
				'name': "SocialCreditNumber",
				'selector_table_sibling': u'社会信用代码'
			}, {
				'name': "CompanyManInCharge",
				'selector_table_sibling': u'企业负责人'
			}, {
				'name': "QualityManInCharge",
				'selector_table_sibling': u'质量负责人'
			}, {
				'name': "ProductionManInCharge",
				'selector_table_sibling': u'生产负责人'
			}, {
				'name': "QualityAuthorizedPerson",
				'selector_table_sibling': u'质量受权人'
			}, {
				'name': "ProductionAddress",
				'selector_table_sibling': u'生产地址'
			}, {
				'name': "InspectionDate",
				'selector_table_sibling': u'检查日期'
			}, {
				'name': "Inspector",
				'selector_table_sibling': u'检查单位'
			}, {
				'name': "InspectionReason",
				'selector_table_sibling': u'事由'
			}, {
				'name': "InspectionResult",
				'selector_table_next_row': u'检查发现问题'
			}, {
				'name': "FollowUpAction",
				'selector_table_next_row': u'处理措施'
			},{
				'name': "$$tempList",
				'strip_tags': False,
				'selector_xpath': '//*/tr/td/table'
			}
			]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

