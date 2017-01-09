#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig

class ScrapyConfig(ScrapyWrapperConfig):
	begin_urls = ["https://s.1688.com/"]
	steps = {
		"begin": {
			'req': {'webview': True},
			'res': {
				'selector': lambda _,__: [ "https://s.1688.com/company/company_search.htm?keywords=%D6%D0%D2%A9%B2%C4&button_click=top&n=y" ],
				'next_step': 'list'
			}
		},
		"list": {
			'req': {'webview': True},
			'res': [{
				'selector_xpath': '//a/@href',
				'selector_regex': '^(https://([a-zA-Z0-9_-]*).1688.com)$',
				'data_postprocessor': lambda url, meta: url + '/page/creditdetail_certificate.htm',
				'next_step': 'content'
			},
			{
				'selector_href_text_contains': u'下一页',
				'next_step': 'list'
			}]
		},
		"content": {
			'req': {'webview': True},
			'res': {
				'selector_href_text_contains': u'进入黄页',
				'next_step': 'basic_info'
			}
		},
		"basic_info": {
			'req': {'webview': True},
			'res': {
				'selector': lambda _,meta: meta['$$url'] + '&tab=companyWeb_BusinessInfo',
				'next_step': 'tab2'
			},
			'fields': [{
				'name': 'CompanyName',
				'selector_css': 'h1.company-name',
				'required': True
			}, {
				'selector_table_sibling': u'主营产品或服务:',
				'name': 'MainProduct',
				'required': True
			}, {
				'selector_table_sibling': u'主营行业:',
				'name': 'MainSector'
			}, {
				'selector_table_sibling': u'经营模式:',
				'name': 'ModeOfOperation'
			}, {
				'selector_table_sibling': u'是否提供加工/定制服务:',
				'name': 'TcmProcessing'
			}, {
				'selector_table_sibling': u'注册资本:',
				'name': 'RegistrationCaptial'
			}, {
				'selector_table_sibling': u'公司成立时间:',
				'name': 'CompanyFoundDate',
				'data_type': 'Date'
			}, {
				'selector_table_sibling': u'企业类型:',	
				'name': 'CompanyType'
			}, {
				'selector_table_sibling': u'法定代表人:',
				'name': 'CorporateRep'
			}, {
				'selector_table_sibling': u'工商注册号;',
				'name': 'RegistrationNumber'
			}, {
				'selector_table_sibling': u'加工方式:',
				'name': 'ProcessingMethod'
			}, {
				'selector_table_sibling': u'工艺:',
				'name': 'CraftInfo'
			}, {
				'selector_table_sibling': u'产品质量认证:',
				'name': 'ProductQualityAuthentication'
			}, {
				'selector_table_sibling': u'员工人数:',
				'name': 'NumberOfEmployee'
			}, {
				'selector_table_sibling': u'研发部门人数:',
				'name': 'RDEmployeeNumber'
			}, {
				'selector_table_sibling': u'厂房面积:',
				'name': 'FacilityArea'
			}, {
				'selector_table_sibling': u'主要销售区域:',
				'name': 'MainSaleRegion'
			}, {
				'selector_table_sibling': u'主要客户群体:',
				'name': 'MainCustomerGroup'
			}, {
				'selector_table_sibling': u'年营业额:',
				'name': 'AnnualSale'
			}, {
				'selector_table_sibling': u'年出口额:',
				'name': 'AnnualExport'
			}, {
				'selector_table_sibling': u'品牌名称:',
				'name': 'BrandName'
			}, {
				'selector_table_sibling': u'质量控制:',
				'name': 'QualityControl'
			}, {
				'selector_table_sibling': u'开户银行:',
				'name': 'MainBank'
			}, {
				'selector_table_sibling': u'账号:',
				'name': 'BankAccountNumber'
			}, {
				'selector_table_sibling': u'公司主页:',
				'name': 'CorporateWebiste'
			}
			]
		},
		'tab2': {
			'req': {'webview': True},
			"res": {
				'selector': lambda _,meta: meta['$$url'].replace('&tab=companyWeb_BusinessInfo', '&tab=companyWeb_contact'),
				'next_step': 'tab3'
			},
			"fields": [{
				'selector_table_sibling': u'90天累计成交笔数',
				'name': 'PastNinetyDaysNumberOfDeal',
				'data_type': 'int'
			}, {
				'selector_table_sibling': u'90天累计买家数',
				'name': 'PastNinetyDaysNumberOfBuyer',
				'data_type': 'int'
			}, {
				'selector_table_sibling': u'买家评价',
				'name': 'BuyerRating',
				'data_type': 'float'
			}, {
				'selector_table_sibling': u'满意率',
				'name': 'SatisfactionRating',
				'data_type': 'percentage'
			}, {
				'selector_table_sibling': u'90天重复采购率',
				'name': 'PastNinetyDaysReturnBuy',
				'data_type': 'percentage'
			}, {
				'selector_table_sibling': u'90天退款率',
				'name': 'PastNinetyDaysReturnOrder',
				'data_type': 'percentage'
			}, {
				'selector_table_sibling': u'90天投诉率',
				'name': 'PastNinetyDaysCompliant',
				'data_type': 'percentage'
			}]
		},
		"tab3": {
			'type': "db",
			'table_name': "TcmTradingCompany",
			'fields': [{
				'selector_table_sibling': u'联系人 :',
				'name': 'ContactPerson'
			}, {
				'selector_table_sibling': u'电话 :',
				'name': 'ContactTelephone'
			}, {
				'selector_table_sibling': u'移动电话 :',
				'name': 'ContactCellphone'
			}, {
				'selector_table_sibling': u'传真 :',
				'name': 'ContactFax'
			}, {
				'selector_table_sibling': u'地址 :',
				'name': 'ContactAddress'
			}, {
				'selector_table_sibling': u'邮编 :',
				'name': 'PostalCode'
			}, {
				'selector_css': 'div.full-content',
				'name': 'CompanyIntroduction'
			}
			]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

