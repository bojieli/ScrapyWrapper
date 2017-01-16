#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig

def enumerate_first_node_type(url, meta):
	map_category = [u'全部', u'重大事项', u'财务报告', u'融资公告', u'风险提示', u'资产重组', u'信息变更', u'持股变动']
	for i in range(0,8):
		meta['ReportType'] = map_category[i]
		yield {
			'url': 'http://data.eastmoney.com/notices/getdata.ashx?StockCode=' + str(url) + '&CodeType=1&PageIndex=1&PageSize=1000&jsObj=wTHYgfuw&SecNodeType=0&FirstNodeType=' + str(i) + '&rt=49484645' 
		}

class ScrapyConfig(ScrapyWrapperConfig):
	custom_settings = {
		'DOWNLOAD_DELAY': 0,
		'CONCURRENT_REQUESTS': 4,
	}
	begin_urls = ["http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=C.BK04651&sty=FCOIATA&sortType=C&sortRule=-1&page=1&pageSize=1000&js=var%20quote_123%3d{rank:[(x)],pages:(pc)}&token=7bc05d0d4c3c22ef9fca8c2a912d779c&jsName=quote_123&_g=0.0603660640467345"]

	steps = {
		"begin": {
			'res': {
			    'parser': 'js-object',
				'selector_json': 'rank',
				'selector': lambda s, meta: s.split(',')[1],
				'next_step': 'list'
			}
		},
		"list": {
			'req': enumerate_first_node_type,
			'res': {
			    'parser': 'js-object',
				'selector_json': 'data',
				'next_step': 'list_parse'
			},
			'fields': [{
				'name': '$$StockCode'
			}]
		},
		"list_parse": {
			'type': 'intermediate',
			'fields': [{
				'name': 'ReportType2',
				'selector_json': 'ANN_RELCOLUMNS.COLUMNNAME',
				'required': True
			}, {
				'name': 'ReportDate',
				'selector_json': 'EUTIME',
				'data_type': 'Date',
				'required': True
			}],
			'res': {
				'selector_json': 'INFOCODE',
				'next_step': 'content',
				'required': True
			},
		},
		"content": {
			'req': {
				'url': lambda url, meta: 'http://data.eastmoney.com/notices/detail/' + meta['$$StockCode'] + '/' + url + ',JUU1JTg1JUI0JUU5JUJEJTkwJUU3JTlDJUJDJUU4JThEJUFG.html'
			},
			'res': {
				'selector_css': 'div.content',
				'next_step': 'db',
				'required': True
			},
		},
		"db": {
			'type': "db",
			'table_name': "PublicCompanyReport",
			'unique': ['CompanyID', 'PdfUrl'],
			'upsert': True,
			'fields': [{
				'name': 'CompanyID',
				'reference': {
					'table': 'PublicCompanyInfo',
					'field': '$$StockCode',
					'remote_field': 'StockCode'
				},
				'required': True
			}, {
				'name': 'ReportNumber',
				'selector_css': 'div.detail-body',
				'selector_regex': u'公告编号：([0-9-]*)'
			}, {
				'name': 'Headline',
				'selector_xpath': '//div[@class="detail-header"]//h1/text()',
				'required': True
			}, {
				'name': 'DetailContent',
				'selector_css': 'div.detail-body',
				'strip_tags': False,
				'download_images': True,
				'required': True
			}, {
				'name': 'PdfUrl',
				'selector_regex': '(http://pdf.dfcfw.com/.*\.pdf)',
				'required': True
			}]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)
