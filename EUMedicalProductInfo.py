#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig

class ScrapyConfig(ScrapyWrapperConfig):
	crawlera_enabled = True

	def url_generator(self):
		for i in range(1,2000):
			#yield 'http://db.yaozh.com/api/index.php/Home/index/yaopinjiage/id/' + str(i)
			yield 'http://db.yaozh.com/epyp/detail?type=ema&id=' + str(i)

	begin_urls = url_generator
	#begin_urls = ["http://db.yaozh.com/api/index.php/Home/index/yaopinzhongbiao/id/3542343"]

	steps = {
		"begin": {
			'res': [{
				'selector_css': 'div.body',
				'next_step': 'db'
            }]
		},
		"db": {
			'type': "db",
			'table_name': "EUMedicalProductInfo",
			'fields': [
{'selector_table_sibling': u'产品编号'		, 'name': "ProductID"},
{'selector_table_sibling': u'商标名'		, 'name': "EURetailName", 'required': True},
{'selector_table_sibling': u'通用名称'		, 'name': "EUGenericName"},
{'selector_table_sibling': u'活性组分'		, 'name': "ActiveComponent"},
{'selector_table_sibling': u'ATC编码'		, 'name': "AtcCode"},
{'selector_table_sibling': u'适应症'		, 'name': "IndicationInfo"},
{'selector_table_sibling': u'孤儿药'		, 'name': "OrphanDrug"},
{'selector_table_sibling': u'通用名药'		, 'name': "GenericDrug"},
{'selector_table_sibling': u'上市许可持有人', 'name': "MarketPermitHolder"},
{'selector_table_sibling': u'状态'			, 'name': "MarketStatus"},
{'selector_table_sibling': u'授权日期'		, 'name': "AuthorizatonDate", 'data_type': 'Date'},
{'selector_table_sibling': u'版本'			, 'name': "VersionNumber"},
{'selector_table_sibling': u'条件批准'		, 'name': "ConditionalApproval"},
{'selector_table_sibling': u'特殊情况'		, 'name': "SpecialCircumstance"},
{'selector_table_sibling': u'生物仿制品'	, 'name': "BiologicalCopy"},
			]
		}
	}


myspider = SpiderFactory(ScrapyConfig(), __name__)
