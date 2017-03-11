#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig

class ScrapyConfig(ScrapyWrapperConfig):
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
			'req': {
				'url': lambda url, meta: 'http://f10.eastmoney.com/f10_v2/ResearchReport.aspx?code=sz' + str(url) + '#gsyb-0',
			},
			'res': {
				'selector_xpath': '//div[@id="gsyb"]/following-sibling::div//li',
				'next_step': 'list_parse'
			},
			'fields': [{
				'name': '$$StockCode'
			}]
		},
		"list_parse": {
			'type': 'intermediate',
			'res': {
				'selector_xpath': '//a/@href',
				'next_step': 'content'
			},
			'fields': [{
				'name': 'Conclusion',
				'selector_xpath': '//span/em',
				'data_postprocessor': lambda n, _: n.strip('[]'),
				'required': True
			}, {
				'name': 'PublicationDate',
				'selector_xpath': '//samp',
				'data_type': 'Date',
				'required': True
			}, {
				'name': 'Headline',
				'selector_xpath': '//a/text()',
				'required': True
			}]
		},
		"content": {
			'res': {
				'selector_css': 'div.newsContent',
				'next_step': 'db'
			},
		},
		"db": {
			'type': "db",
			'table_name': "PublicCompanyResearchReportAndRating",
			'unique': ['CompanyID', 'PublicationDate', 'Headline'],
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
				'name': 'DetailContent',
				'strip_tags': False,
				'download_images': True,
				'required': True
			}]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)
