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
				'next_step': 'content'
			}
		},
		"content": {
			'req': {
				'url': lambda url, meta: 'http://f10.eastmoney.com/f10_v2/CompanySurvey.aspx?code=sz' + str(url)
			},
			'res': {
				'selector_css': 'body > div.main',
				'keep_html_tags': True,
				'next_step': 'db'
			},
			'fields': [{
				'name': "StockCode",
				'selector': lambda url, meta: url,
				'required': True
			}]
		},
		"db": {
			'type': "db",
			'table_name': "PublicCompanyInfo",
			'unique': ['StockCode'],
			'upsert': True,
			'fields': [{
				'name': "ChineseName",
				'selector_table_sibling_contains': u'公司名称',
				'required': True
			}, {
				'name': "EnglishName",
				'selector_table_sibling_contains': u'英文名称'
			}, {
				'name': "PreviousName",
				'selector_table_sibling_contains': u'曾用名'
			}, {
				'name': "StockSymbol",
				'selector_table_sibling_contains': u'A股简称'
			}, {
				'name': "StockType",
				'selector_table_sibling_contains': u'证券类别'
			}, {
				'name': "StockSector",
				'selector_table_sibling_contains': u'所属行业'
			}, {
				'name': "GeneralManager",
				'selector_table_sibling_contains': u'总经理'
			}, {
				'name': "CorporateRep",
				'selector_table_sibling_contains': u'法人代表'
			}, {
				'name': "ChairmanSecretary",
				'selector_table_sibling_contains': u'董秘'
			}, {
				'name': "Chairman",
				'selector_table_sibling_contains': u'董事长'
			}, {
				'name': "FinancialMarketRep",
				'selector_table_sibling_contains': u'证券事务代表'
			}, {
				'name': "IndependentDirector",
				'selector_table_sibling_contains': u'独立董事'
			}, {
				'name': "ContactTelephone",
				'selector_table_sibling_contains': u'联系电话'
			}, {
				'name': "ContactEmail",
				'selector_table_sibling_contains': u'电子信箱'
			}, {
			    'name': "ContactFax",
			    'selector_table_sibling_contains': u'传真'
			}, {
			    'name': "CorporateWebsite",
			    'selector_table_sibling_contains': u'公司网址'
			}, {
			    'name': "CorporateAddress",
			    'selector_table_sibling_contains': u'办公地址'
			}, {
			    'name': "RegistrationAddress",
			    'selector_table_sibling_contains': u'注册地址'
			}, {
			    'name': "Region",
			    'selector_table_sibling_contains': u'区域'
			}, {
			    'name': "RegionID",
			    'reference': { 'field': 'Region', 'match': 'address' },
				'required': True
			}, {
			    'name': "PostalCode",
			    'selector_table_sibling_contains': u'邮政编码'
			}, {
			    'name': "RegistrationCaptial",
			    'selector_table_sibling_contains': u'注册资本'
			}, {
			    'name': "RegistrationNumber",
			    'selector_table_sibling_contains': u'工商登记'
			}, {
			    'name': "NumberOfEmployee",
			    'selector_table_sibling_contains': u'雇员人数'
			}, {
			    'name': "NumberOfManagement",
			    'selector_table_sibling_contains': u'管理人员人数'
			}, {
			    'name': "LawFirm",
			    'selector_table_sibling_contains': u'律师事务所'
			}, {
			    'name': "AccountingFirm",
			    'selector_table_sibling_contains': u'会计师事务所'
			}, {
			    'name': "CompanyIntro",
			    'selector_table_sibling_contains': u'公司简介'
			}, {
			    'name': "ScopeOfOperation",
			    'selector_table_sibling_contains': u'经营范围'
			}, {
			    'name': "DateOfCreation",
			    'selector_table_sibling_contains': u'成立日期',
				'data_type': 'Date'
			}, {
			    'name': "ListingDate",
			    'selector_table_sibling_contains': u'上市日期',
				'data_type': 'Date'
			}, {
			    'name': "PERatio",
			    'selector_table_sibling_contains': u'发行市盈率',
				'data_type': 'float'
			}, {
			    'name': "InternetOfferingDate",
			    'selector_table_sibling_contains': u'网上发行日期',
				'data_type': 'Date'
			}, {
			    'name': "OfferingType",
			    'selector_table_sibling_contains': u'发行方式'
			}, {
			    'name': "StockFaceValue",
			    'selector_table_sibling_contains': u'每股面值',
				'data_type': 'float'
			}, {
			    'name': "SizeOfOffering",
			    'selector_table_sibling_contains': u'发行量',
				'data_type': 'int'
			}, {
			    'name': "IssuePrice",
			    'selector_table_sibling_contains': u'每股发行价',
				'data_type': 'float'
			}, {
			    'name': "CostOfOffering",
			    'selector_table_sibling_contains': u'发行费用',
				'data_type': 'float'
			}, {
			    'name': "OfferingCapitalization",
			    'selector_table_sibling_contains': u'发行总市值',
				'data_type': 'float',
				'required': True
			}, {
			    'name': "RaisedCapital",
			    'selector_table_sibling_contains': u'募集资金净额',
				'data_type': 'float'
			}, {
			    'name': "FirstDayOpeningPrice",
			    'selector_table_sibling_contains': u'首日开盘价',
				'data_type': 'float'
			}, {
			    'name': "FirstDayClosingPrice",
			    'selector_table_sibling_contains': u'首日收盘价',
				'data_type': 'float'
			}, {
			    'name': "FirstDayTurnoverRatio",
			    'selector_table_sibling_contains': u'首日换手率',
				'data_type': 'percentage'
			}, {
			    'name': "FirstDayHighestPrice",
			    'selector_table_sibling_contains': u'首日最高价',
				'data_type': 'float'
			}, {
			    'name': "LotWinningRate",
			    'selector_table_sibling_contains': u'网下配售中签率',
				'data_type': 'percentage'
			}, {
			    'name': "SetPriceLotWinningRate",
			    'selector_table_sibling_contains': u'定价中签率',
				'data_type': 'percentage'
			}
			]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

