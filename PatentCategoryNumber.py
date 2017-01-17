#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
import datetime

formdata = 'ID=SCPD&hdnSearchType=&hdnIsAll=false&NaviField=%E4%B8%93%E9%A2%98%E5%AD%90%E6%A0%8F%E7%9B%AE%E4%BB%A3%E7%A0%81&NaviDatabaseName=SCPD_ZJCLS&systemno=&hdnFathorCode=sysAll&selectbox=E&strNavigatorValue=%2CA%2CB%2CC%2CD%2CE%2CF%2CH%2CI&strNavigatorName=%2C%E5%9F%BA%E7%A1%80%E7%A7%91%E5%AD%A6%2C%E5%B7%A5%E7%A8%8B%E7%A7%91%E6%8A%80%E2%85%A0%E8%BE%91%2C%E5%B7%A5%E7%A8%8B%E7%A7%91%E6%8A%80%E2%85%A1%E8%BE%91%2C%E5%86%9C%E4%B8%9A%E7%A7%91%E6%8A%80%2C%E5%8C%BB%E8%8D%AF%E5%8D%AB%E7%94%9F%E7%A7%91%E6%8A%80%2C%E5%93%B2%E5%AD%A6%E4%B8%8E%E4%BA%BA%E6%96%87%E7%A7%91%E5%AD%A6%2C%E7%A4%BE%E4%BC%9A%E7%A7%91%E5%AD%A6%E2%85%A1%E8%BE%91%2C%E4%BF%A1%E6%81%AF%E7%A7%91%E6%8A%80&singleleafcode=&searchAttachCondition=&SearchQueryID=&SearchFieldRelationDirectory=&updateTempDB=&bCurYearTempDB=1&fieldtips=%E7%AF%87%E5%90%8D%2F%5B%E5%9C%A8%E6%96%87%E7%8C%AE%E6%A0%87%E9%A2%98%E4%B8%AD%E6%A3%80%E7%B4%A2%E3%80%82%E5%AF%B9%E8%AF%A5%E6%A3%80%E7%B4%A2%E9%A1%B9%E7%9A%84%E6%A3%80%E7%B4%A2%E6%98%AF%E6%8C%89%E8%AF%8D%E8%BF%9B%E8%A1%8C%E7%9A%84%EF%BC%8C%E8%AF%B7%E5%B0%BD%E5%8F%AF%E8%83%BD%E8%BE%93%E5%85%A5%E5%AE%8C%E6%95%B4%E7%9A%84%E8%AF%8D%EF%BC%8C%E4%BB%A5%E9%81%BF%E5%85%8D%E6%BC%8F%E6%A3%80%E3%80%82%5D%2C%E5%85%B3%E9%94%AE%E8%AF%8D%2F%5B%E6%A3%80%E7%B4%A2%E6%96%87%E7%8C%AE%E7%9A%84%E5%85%B3%E9%94%AE%E8%AF%8D%E4%B8%AD%E6%BB%A1%E8%B6%B3%E6%A3%80%E7%B4%A2%E6%9D%A1%E4%BB%B6%E7%9A%84%E6%96%87%E7%8C%AE%E3%80%82%E5%AF%B9%E8%AF%A5%E6%A3%80%E7%B4%A2%E9%A1%B9%E7%9A%84%E6%A3%80%E7%B4%A2%E6%98%AF%E6%8C%89%E8%AF%8D%E8%BF%9B%E8%A1%8C%E7%9A%84%EF%BC%8C%E8%AF%B7%E5%B0%BD%E5%8F%AF%E8%83%BD%E8%BE%93%E5%85%A5%E5%AE%8C%E6%95%B4%E7%9A%84%E8%AF%8D%EF%BC%8C%E4%BB%A5%E9%81%BF%E5%85%8D%E6%BC%8F%E6%A3%80%E3%80%82%5D%2C%E7%AC%AC%E4%B8%80%E8%B4%A3%E4%BB%BB%E4%BA%BA%2F%5B%E8%AF%B7%E9%80%89%E6%8B%A9%E6%A3%80%E7%B4%A2%E9%A1%B9%E5%B9%B6%E6%8C%87%E5%AE%9A%E7%9B%B8%E5%BA%94%E7%9A%84%E6%A3%80%E7%B4%A2%E8%AF%8D%EF%BC%8C%E9%80%89%E6%8B%A9%E6%8E%92%E5%BA%8F%E6%96%B9%E5%BC%8F%E3%80%81%E5%8C%B9%E9%85%8D%E6%A8%A1%E5%BC%8F%E3%80%81%E6%96%87%E7%8C%AE%E6%97%B6%E9%97%B4%E7%AD%89%E9%99%90%E5%AE%9A%E6%9D%A1%E4%BB%B6%EF%BC%8C%E7%84%B6%E5%90%8E%E7%82%B9%E5%87%BB%E2%80%9C%E6%A3%80%E7%B4%A2%E2%80%9D%E3%80%82%5D%2C%E4%BD%9C%E8%80%85%2F%5B%E5%8F%AF%E8%BE%93%E5%85%A5%E4%BD%9C%E8%80%85%E5%AE%8C%E6%95%B4%E5%A7%93%E5%90%8D%EF%BC%8C%E6%88%96%E5%8F%AA%E8%BE%93%E5%85%A5%E8%BF%9E%E7%BB%AD%E7%9A%84%E4%B8%80%E9%83%A8%E5%88%86%E3%80%82%5D%2C%E6%9C%BA%E6%9E%84%2F%5B%E5%8F%AF%E8%BE%93%E5%85%A5%E5%AE%8C%E6%95%B4%E7%9A%84%E6%9C%BA%E6%9E%84%E5%90%8D%E7%A7%B0%EF%BC%8C%E6%88%96%E5%8F%AA%E8%BE%93%E5%85%A5%E8%BF%9E%E7%BB%AD%E7%9A%84%E4%B8%80%E9%83%A8%E5%88%86%E3%80%82%5D%2C%E4%B8%AD%E6%96%87%E6%91%98%E8%A6%81%2F%5B%E5%AF%B9%E8%AF%A5%E6%A3%80%E7%B4%A2%E9%A1%B9%E7%9A%84%E6%A3%80%E7%B4%A2%E6%98%AF%E6%8C%89%E8%AF%8D%E8%BF%9B%E8%A1%8C%E7%9A%84%EF%BC%8C%E8%AF%B7%E5%B0%BD%E5%8F%AF%E8%83%BD%E8%BE%93%E5%85%A5%E5%AE%8C%E6%95%B4%E7%9A%84%E8%AF%8D%EF%BC%8C%E4%BB%A5%E9%81%BF%E5%85%8D%E6%BC%8F%E6%A3%80%E3%80%82%5D%2C%E5%BC%95%E6%96%87%2F%5B%E8%AF%B7%E9%80%89%E6%8B%A9%E6%A3%80%E7%B4%A2%E9%A1%B9%E5%B9%B6%E6%8C%87%E5%AE%9A%E7%9B%B8%E5%BA%94%E7%9A%84%E6%A3%80%E7%B4%A2%E8%AF%8D%EF%BC%8C%E9%80%89%E6%8B%A9%E6%8E%92%E5%BA%8F%E6%96%B9%E5%BC%8F%E3%80%81%E5%8C%B9%E9%85%8D%E6%A8%A1%E5%BC%8F%E3%80%81%E6%96%87%E7%8C%AE%E6%97%B6%E9%97%B4%E7%AD%89%E9%99%90%E5%AE%9A%E6%9D%A1%E4%BB%B6%EF%BC%8C%E7%84%B6%E5%90%8E%E7%82%B9%E5%87%BB%E2%80%9C%E6%A3%80%E7%B4%A2%E2%80%9D%E3%80%82%5D%2C%E5%85%A8%E6%96%87%2F%E8%AF%B7%E9%80%89%E6%8B%A9%E6%A3%80%E7%B4%A2%E9%A1%B9%E5%B9%B6%E6%8C%87%E5%AE%9A%E7%9B%B8%E5%BA%94%E7%9A%84%E6%A3%80%E7%B4%A2%E8%AF%8D%EF%BC%8C%E9%80%89%E6%8B%A9%E6%8E%92%E5%BA%8F%E6%96%B9%E5%BC%8F%E3%80%81%E5%8C%B9%E9%85%8D%E6%A8%A1%E5%BC%8F%E3%80%81%E6%96%87%E7%8C%AE%E6%97%B6%E9%97%B4%E7%AD%89%E9%99%90%E5%AE%9A%E6%9D%A1%E4%BB%B6%EF%BC%8C%E7%84%B6%E5%90%8E%E7%82%B9%E5%87%BB%E2%80%9C%E6%A3%80%E7%B4%A2%E2%80%9D%E3%80%82%5D%2C%E5%9F%BA%E9%87%91%2F%5B%E6%A3%80%E7%B4%A2%E5%8F%97%E6%BB%A1%E8%B6%B3%E6%9D%A1%E4%BB%B6%E7%9A%84%E5%9F%BA%E9%87%91%E8%B5%84%E5%8A%A9%E7%9A%84%E6%96%87%E7%8C%AE%E3%80%82%5D%2C%E4%B8%AD%E6%96%87%E5%88%8A%E5%90%8D%2F%5B%E8%AF%B7%E8%BE%93%E5%85%A5%E9%83%A8%E5%88%86%E6%88%96%E5%85%A8%E9%83%A8%E5%88%8A%E5%90%8D%E3%80%82%5D%2CISSN%2F%5B%E8%AF%B7%E8%BE%93%E5%85%A5%E5%AE%8C%E6%95%B4%E7%9A%84ISSN%E5%8F%B7%E3%80%82%5D%2C%E5%B9%B4%2F%5B%E8%BE%93%E5%85%A5%E5%9B%9B%E4%BD%8D%E6%95%B0%E5%AD%97%E7%9A%84%E5%B9%B4%E4%BB%BD%E3%80%82%5D%2C%E6%9C%9F%2F%5B%E8%BE%93%E5%85%A5%E6%9C%9F%E5%88%8A%E7%9A%84%E6%9C%9F%E5%8F%B7%EF%BC%8C%E5%A6%82%E6%9E%9C%E4%B8%8D%E8%B6%B3%E4%B8%A4%E4%BD%8D%E6%95%B0%E5%AD%97%EF%BC%8C%E8%AF%B7%E5%9C%A8%E5%89%8D%E9%9D%A2%E8%A1%A5%E2%80%9C0%E2%80%9D%EF%BC%8C%E5%A6%82%E2%80%9C08%E2%80%9D%E3%80%82%5D%2C%E4%B8%BB%E9%A2%98%2F%5B%E4%B8%BB%E9%A2%98%E5%8C%85%E6%8B%AC%E7%AF%87%E5%90%8D%E3%80%81%E5%85%B3%E9%94%AE%E8%AF%8D%E3%80%81%E4%B8%AD%E6%96%87%E6%91%98%E8%A6%81%E3%80%82%E5%8F%AF%E6%A3%80%E7%B4%A2%E5%87%BA%E8%BF%99%E4%B8%89%E9%A1%B9%E4%B8%AD%E4%BB%BB%E4%B8%80%E9%A1%B9%E6%88%96%E5%A4%9A%E9%A1%B9%E6%BB%A1%E8%B6%B3%E6%8C%87%E5%AE%9A%E6%A3%80%E7%B4%A2%E6%9D%A1%E4%BB%B6%E7%9A%84%E6%96%87%E7%8C%AE%E3%80%82%E5%AF%B9%E4%B8%BB%E9%A2%98%E6%98%AF%E6%8C%89%E8%AF%8D%E6%A3%80%E7%B4%A2%E7%9A%84%EF%BC%8C%E8%AF%B7%E5%B0%BD%E5%8F%AF%E8%83%BD%E8%BE%93%E5%85%A5%E5%AE%8C%E6%95%B4%E7%9A%84%E8%AF%8D%EF%BC%8C%E4%BB%A5%E9%81%BF%E5%85%8D%E6%BC%8F%E6%A3%80%E3%80%82%5D&advancedfield1=%E5%85%B3%E9%94%AE%E8%AF%8D&advancedvalue1=%E4%B8%AD%E8%8D%AF&imageField.x=11&imageField.y=16&searchmatch=0&order=dec&RecordsPerPage=20&hdnUSPSubDB=%E4%B8%93%E5%88%A9%E7%B1%BB%E5%88%AB%2C%2B1%2B2%2B3%2B%2C3%2C3&TableType=PY&display=chinese&encode=gb&TablePrefix=SCPD&View=SCPD&yearFieldName=%E5%B9%B4&userright=&VarNum=1&MM_slt_updateTime=&MM_Update_Time=&MM_Update_EndTime=&MM_fieldValue_2_1=&MM_fieldValue_2_2=&MM_hiddenTxtName=MM_fieldValue_1_1%40%40%40MM_fieldValue_1_2%40%40%40MM_fieldValue_2_1%40%40%40MM_fieldValue_2_2%40%40%40MM_Update_Time%40%40%40MM_Update_EndTime&MM_fieldName=%E7%94%B3%E8%AF%B7%E6%97%A5%40%40%40%E7%94%B3%E8%AF%B7%E6%97%A5%40%40%40%E5%85%AC%E5%BC%80%E6%97%A5%40%40%40%E5%85%AC%E5%BC%80%E6%97%A5%40%40%40%E6%9B%B4%E6%96%B0%E6%97%A5%E6%9C%9F%40%40%40%E6%9B%B4%E6%96%B0%E6%97%A5%E6%9C%9F&MM_hiddenRelation=%3E%3D%40%40%40%3C%3D%40%40%40%3E%3D%40%40%40%3C%3D%40%40%40%3E%3D%40%40%40%3C%3D'

def gen_date():
	day_count = 10000
	start_date = datetime.datetime.today()
	end_date = datetime.datetime.strptime('1990-01-01', '%Y-%m-%d')
	curr_date = start_date
	while curr_date > end_date:
		yield curr_date
		curr_date -= datetime.timedelta(days=10)
	yield end_date

def gen_req(url, meta):
	req_conf = {
		'url': url,
		'meta': meta,
		'method': 'post',
		'headers': {'Content-Type': 'application/x-www-form-urlencoded'},
		'dont_filter': True
	}
	last_date = None
	for date in gen_date():
		if not last_date:
			last_date = date
			continue
		to_date = last_date.strftime('%Y-%m-%d')
		from_date = (date + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
		req_conf['post_rawdata'] = formdata + "&MM_fieldValue_1_1=" + from_date + "&MM_fieldValue_1_2=" + to_date
		print(from_date, to_date)
		yield req_conf
		last_date = date

	if last_date:
		req_conf['post_rawdata'] = formdata + "&MM_fieldValue_1_1=" + "&MM_fieldValue_1_2=" + last_date.strftime('%Y-%m-%d')
		yield req_conf 

class ScrapyConfig(ScrapyWrapperConfig):
	crawlera_enabled = True

	begin_urls = ["http://dbpub.cnki.net/Grid2008/Dbpub/Brief.aspx?ID=SCPD&subBase=all"]

	steps = {
		"begin": {
			'req': gen_req,
			'res': [{
				'selector_css': 'table.s_table tr',
				'next_step': 'list'
			}, {
				'selector_href_text': u'下页',
				'next_step': 'morepages'
			}]
		},
		"morepages": {
			'req': { 'dont_filter': True },
			'res': [{
				'selector_css': 'table.s_table tr',
				'next_step': 'list'
			}, {
				'selector_href_text': u'下页',
				'next_step': 'morepages'
			}]
		},
		"list": {
			'type': 'intermediate',
			'res': {
				'selector_xpath': '//td[1]/a/@href',
				'next_step': 'content'
			}
		},
		"content": {
			'res': {
				'selector_xpath': '//body',
				'next_step': 'db'
			}
		},
		"db": {
			'type': "db",
			'table_name': "PatentCategoryNumber",
			'unique': ['ApplicationID'],
			'upsert': True,
			'fields': [{
				'name': 'PatentName',
				'selector_xpath': '//td[@style = "font-size:18px;font-weight:bold;text-align:center;"]',
				'required': True
			}, {
				'selector_table_sibling_contains': u'发明人',
				'name': 'InventorName',
				'required': True
			}, {
				'selector_table_sibling_contains': u'申请人',
				'name': 'PatentApplicant'
			}, {
				'selector_table_sibling_contains': u'申请日',
				'name': 'ApplicationDate',
				'data_type': 'Date'
			}, {
				'selector_table_sibling_contains': u'公开日',
				'name': 'PublicationDate',
				'data_type': 'Date'
			}, {
				'selector_table_sibling_contains': u'申请号',
				'name': 'ApplicationID',
				'required': True
			}, {
				'selector_table_sibling_contains': u'公开号',
				'name': 'PublicationID'
			}, {
				'selector_table_sibling_contains': u'地址',
				'name': 'CurrentAddress'
			}, {
				'selector_table_sibling_contains': u'地址',
				'name': '$$Address',
				'data_postprocessor': lambda d,_: d.lstrip('0123456789 ')
			}, {
				'name': 'RegionID',
				'reference': { 'field': '$$Address', 'table': 'TB_Addresses', 'remote_field': 'Name', 'remote_id_field': 'PID', 'match': 'lpm' }
			}, {
				'selector_table_sibling_contains': u'国省代码',
				'name': 'CountryProvinceID'
			}, {
				'selector_table_sibling_contains': u'摘要',
				'name': 'PatentDescription'
			}, {
				'selector_table_sibling_contains': u'主权项',
				'name': 'IndependentClaim'
			}, {
				'selector_table_sibling_contains': u'页数',
				'name': 'PageNumber'
			}, {
				'selector_table_sibling_contains': u'主分类号',
				'name': 'MainCategoryNumber'
			}, {
				'selector_table_sibling_contains': u'专利分类号',
				'name': 'PatentCategoryNumber'
			}
			]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

