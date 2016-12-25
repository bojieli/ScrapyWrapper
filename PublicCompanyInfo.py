#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderWrapper
from scrapywrapper.config import ScrapyWrapperConfig

class ScrapyConfig(ScrapyWrapperConfig):
	begin_urls = ["http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=C.BK04651&sty=FCOIATA&sortType=C&sortRule=-1&page=1&pageSize=1000&js=var%20quote_123%3d{rank:[(x)],pages:(pc)}&token=7bc05d0d4c3c22ef9fca8c2a912d779c&jsName=quote_123&_g=0.0603660640467345"]
	steps = {
		"begin": {
			'res': {
			    'parser': 'js-string',
				'selector': lambda s: s.split(',')[1],
				'next_step': 'content'
			}
		},
		"content": {
			'req': {
				'url': lambda url, meta: 'http://f10.eastmoney.com/f10_v2/CompanySurvey.aspx?code=sz' + str(url)
			},
			'res': {
				'selector_css': 'body > div.main > div.section.first',
				'keep_html_tags': True,
				'next_step': 'db'
			}
		},
		"db": {
			'type': "db",
			'table_name': "PublicCompanyInfo",
			'fields': [{
				'name': "ChineseName",
				'selector_table_sibling': u'中文名称'
			}, {
				'name': "EnglishName",
				'selector_table_sibling': u'英文名称'
			}, {
				'name': "PreviousName",
				'selector_table_sibling': u'曾用名'
			}, {
				'name': "StockCode",
				'selector_table_sibling': u'股票代码'
			}, {
				'name': "StockSymbol",
				'selector_table_sibling': u'股票简称'
			}, {
				'name': "StockType",
				'selector_table_sibling': u'股票简称'
			}, {
				'name': "StockSector",
				'selector_table_sibling': u'证券类别'
			}, {
				'name': "StockSector",
				'selector_table_sibling': u'所属行业'
			}, {
				'name': "GeneralManager",
				'selector_table_sibling': u'总经理'
			}, {
				'name': "CorporateRep",
				'selector_table_sibling': u'法人代表'
			}, {
				'name': "ChairmanSecretary",
				'selector_table_sibling': u'董秘'
			}, {
				'name': "Chairman",
				'selector_table_sibling': u'董事长'
			}, {
				'name': "FinancialMarketCap",
				'selector_table_sibling': u'证券事务代表'
			}, {
				'name': "IndependentDirector",
				'selector_table_sibling': u'独立董事'
			}, {
				'name': "ContactTelephone",
				'selector_table_sibling': u'联系电话'
			}, {
				'name': "ContactEmail",
				'selector_table_sibling': u'电子信箱'
			}, {
			    'name': "ContactFax",
			    'selector_table_sibling': u'传真'
			}, {
			    'name': "CorporateWebsite",
			    'selector_table_sibling': u'公司网址'
			}, {
			    'name': "CorporateAddress",
			    'selector_table_sibling': u'办公地址'
			}, {
			    'name': "RegistrationAddress",
			    'selector_table_sibling': u'注册地址'
			}, {
			    'name': "Region",
			    'selector_table_sibling': u'区域'
			}, {
			    'name': "RegionID",
			    'selector_table_sibling': u'区域ID'
			}, {
			    'name': "PostalCode",
			    'selector_table_sibling': u'邮政编码'
			}, {
			    'name': "RegistrationCaptial",
			    'selector_table_sibling': u'注册资本'
			}, {
			    'name': "RegistrationNumber",
			    'selector_table_sibling': u'工商登记'
			}, {
			    'name': "NumberOfEmployee",
			    'selector_table_sibling': u'雇员人数'
			}, {
			    'name': "NumberOfManagement",
			    'selector_table_sibling': u'管理人员人数'
			}, {
			    'name': "LawFirm",
			    'selector_table_sibling': u'律师事务所'
			}, {
			    'name': "AccountingFirm",
			    'selector_table_sibling': u'会计师事务所'
			}, {
			    'name': "CompanyIntro",
			    'selector_table_sibling': u'公司简介'
			}, {
			    'name': "ScopeOfOperation",
			    'selector_table_sibling': u'经营范围'
			}, {
			    'name': "DateOfCreation",
			    'selector_table_sibling': u'成立日期',
				'data_type': 'Date'
			}, {
			    'name': "ListingDate",
			    'selector_table_sibling': u'上市日期',
				'data_type': 'Date'
			}, {
			    'name': "PERatio",
			    'selector_table_sibling': u'发行市盈率',
				'data_type': 'float'
			}, {
			    'name': "InternetOfferingDate",
			    'selector_table_sibling': u'网上发行日期',
				'data_type': 'float'
			}, {
			    'name': "OfferingType",
			    'selector_table_sibling': u'发行方式'
			}, {
			    'name': "StockFaceValue",
			    'selector_table_sibling': u'每股面值',
				'data_type': 'float'
			}, {
			    'name': "SizeOfOffering",
			    'selector_table_sibling': u'发行量(股)',
				'data_type': 'int'
			}, {
			    'name': "IssuePrice",
			    'selector_table_sibling': u'每股发行价(元)',
				'data_type': 'float'
			}, {
			    'name': "CostOfOffering",
			    'selector_table_sibling': u'发行费用(元)',
				'data_type': 'float'
			}, {
			    'name': "OfferingCapitalization",
			    'selector_table_sibling': u'发行总市值(元)',
				'data_type': 'float'
			}, {
			    'name': "RaisedCapital",
			    'selector_table_sibling': u'募集资金净额(元)',
				'data_type': 'float'
			}, {
			    'name': "FirstDayOpeningPrice",
			    'selector_table_sibling': u'首日开盘价(元)',
				'data_type': 'float'
			}, {
			    'name': "FirstDayClosingPrice",
			    'selector_table_sibling': u'首日收盘价(元)',
				'data_type': 'float'
			}, {
			    'name': "FirstDayTurnoverRatio",
			    'selector_table_sibling': u'首日换手率',
				'data_type': 'percentage'
			}, {
			    'name': "FirstDayHighestPrice",
			    'selector_table_sibling': u'首日最高价(元)',
				'data_type': 'float'
			}, {
			    'name': "LotWinningRate",
			    'selector_table_sibling': u'网下配售中签率',
				'data_type': 'percentage'
			}, {
			    'name': "SetPriceLotWinningRate",
			    'selector_table_sibling': u'定价中签率',
				'data_type': 'percentage'
			}
			]
		}
	}

class Spider(SpiderWrapper):
	config = ScrapyConfig()

