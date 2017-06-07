#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
from urlparse import urljoin
import sys

def parse_DrugName_Filter(str_temp):
    find_flag=0
    if str_temp.find(u'限制')>=0:
        find_flag = str_temp.find(u'限制')
        str_temp=str_temp[find_flag+2:]
        if str_temp.find(u'适应症') >= 0:
            find_flag = str_temp.find(u'适应症')
            str_temp = str_temp[:find_flag]
        #print '-----------', str_temp
    elif str_temp.find(u'关注')>=0:
        find_flag = str_temp.find(u'关注')
        str_temp=str_temp[find_flag+2:]
        #print '-----------', str_temp
    elif str_temp.find(u'警惕')>=0:
        find_flag = str_temp.find(u'警惕')
        str_temp = str_temp[find_flag + 2:]

        if str_temp.find(u'超剂量使用') >= 0:
            find_flag = str_temp.find(u'超剂量使用')
            str_temp = str_temp[find_flag + 5:]

        if str_temp.find(u'群体服用') >= 0:
            find_flag = str_temp.find(u'群体服用')
            str_temp = str_temp[find_flag + 4:]
        #print '-----------', str_temp
    elif str_temp.find(u'关于')>=0:
        find_flag = str_temp.find(u'关于')
        str_temp = str_temp[find_flag + 2:]
        print '-----------', str_temp
    elif str_temp.find(u'期） ')>=0:
        find_flag = str_temp.find(u'期） ')
        str_temp = str_temp[find_flag + 3:]
        #print '-----------', str_temp
    else:
        pass


    if str_temp.find(u'引起的')>=0:
        find_flag = str_temp.find(u'引起的')
        str_temp=str_temp[:find_flag]
        if str_temp.find(u'补碘') >= 0:
            find_flag = str_temp.find(u'补碘')
            str_temp = str_temp[:find_flag]
        #print '++++++++++++', str_temp
    elif str_temp.find(u'的严重')>=0:
        find_flag = str_temp.find(u'的严重')
        str_temp = str_temp[:find_flag]
        #print '++++++++++++', str_temp
    elif str_temp.find(u'的')>=0:
        find_flag = str_temp.find(u'的')
        str_temp = str_temp[:find_flag]
        if str_temp.find(u'可能') >= 0:
            find_flag = str_temp.find(u'可能')
            str_temp = str_temp[:find_flag]
        if str_temp.find(u'临床') >= 0:
            find_flag = str_temp.find(u'临床')
            str_temp = str_temp[:find_flag]
        #print '++++++++++++', str_temp
    elif str_temp.find(u'严重')>=0:
        find_flag = str_temp.find(u'严重')
        str_temp = str_temp[:find_flag]
        #print '++++++++++++', str_temp
    elif str_temp.find(u'可能')>=0:
        find_flag = str_temp.find(u'可能')
        str_temp = str_temp[:find_flag]
        #print '++++++++++++', str_temp
    elif str_temp.find(u'联合使用')>=0:
        find_flag = str_temp.find(u'联合使用')
        str_temp = str_temp[:find_flag]
        #print '++++++++++++', str_temp
    elif str_temp.find(u'导致')>=0:
        find_flag = str_temp.find(u'导致')
        str_temp = str_temp[:find_flag]
        #print '++++++++++++', str_temp
    elif str_temp.find(u'治疗过程')>=0:
        find_flag = str_temp.find(u'治疗过程')
        str_temp = str_temp[:find_flag]
        #print '++++++++++++', str_temp
    elif str_temp.find(u'与')>=0:
        find_flag = str_temp.find(u'与')
        str_temp = str_temp[:find_flag]
        #print '++++++++++++', str_temp
    elif str_temp.find(u'引起')>=0:
        find_flag = str_temp.find(u'引起')
        str_temp = str_temp[:find_flag]
        #print '++++++++++++', str_temp
    elif str_temp.find(u'补碘')>=0:
        find_flag = str_temp.find(u'补碘')
        str_temp = str_temp[:find_flag]
        #print '++++++++++++', str_temp
    elif str_temp.find(u'血糖异常不良反应及')>=0:
        find_flag = str_temp.find(u'血糖异常不良反应及')
        str_temp = str_temp[:find_flag]
        #print '++++++++++++', str_temp
    else:
        pass

    #碘普罗胺注射液和红花注射液
    if str_temp.find(u'和')>=0:
        str_temp = str_temp.replace(u'和',u'、')
        #print '++++++++++++', str_temp
    else:
        pass
    return str_temp

def parse_DrugName(meta):
	if 'ClassificationNumber' in meta and meta['ClassificationNumber']:
		type_num=meta['ClassificationNumber']
		if type_num!='1':
			return meta
		#DetailContent Headline
		temp=meta['Headline']
		if 'DrugName' in meta:
			s_temp = ''
			if temp.find(u'，') >= 0:
				list_temp = temp.split(u'，')
				for s in list_temp:
					s_temp = s_temp + u'、' + parse_DrugName_Filter(s)
				s_temp = s_temp[1:]
			elif temp.find(u'、') >= 0:
				list_temp = temp.split(u'、')
				for s in list_temp:
					s_temp = s_temp + u'、' + parse_DrugName_Filter(s)
				s_temp = s_temp[1:]
			elif temp.find(u'与') >= 0:
				list_temp = temp.split(u'与')
				for s in list_temp:
					s_temp = s_temp + u'、' + parse_DrugName_Filter(s)
				s_temp = s_temp[1:]
			else:
				s_temp = parse_DrugName_Filter(temp)

			if s_temp.find(u'病例报告') >= 0:
				s_temp = ''
			if s_temp.find(u'年度报告') >= 0:
				s_temp = ''
			print u'整理：：：：', s_temp
			print '*****************************************',meta['DrugName']
			meta['DrugName']=s_temp
			return meta


base_url = "http://www.sda.gov.cn/WS01/"

class ScrapyConfig(ScrapyWrapperConfig):
	begin_urls = ["CL1060/", "CL1061/", "CL1063/", "CL1064/"]
	steps = {
		"begin": {
			'req': {
				'url': lambda url, meta: urljoin(base_url, url) if url.startswith('CL') else url,
			},
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
			'fields': [{
				'name': "ClassificationNumber",
				'data_preprocessor': lambda _, meta: meta['$$referer'],
				'selector_regex': 'CL([0-9]*)',
				'data_postprocessor': lambda n, meta: '1' if n == '1060' else '2' if n == '1061' else '3' if n == '1063' else '4' if n == '1064' else None,
				'required': True
			}],
			'res': {
				'selector_xpath': '/html/body/table[2]/tbody/tr/td/table',
				'next_step': 'db',
				'required': True
			}
		},
		"db": {
			'type': "db",
			'table_name': "DrugSafetyWarning",
			'unique': ['PublicationDate', 'Headline'],
			'postprocessor': parse_DrugName,
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
				'name': "DrugName",
				'selector_table_sibling': u'药品名称'
			}, {
				'name': "DetailContent",
				'selector_css': 'td.articlecontent3',
				'strip_tags': False,
				'download_images': True
			}
			]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

