#/usr/bin/python
from ../wrapper import SpiderWrapper
from ../config import ScrapyWrapperConfig

class ScrapyConfig(ScrapyWrapperConfig):
	begin_urls = ["http://www.sda.gov.cn/WS01/CL1850/"]
	steps = {
		"begin": {
			res: [{
				selector_css: 'a::attr(href)',
				selector_regex: '(\.\./CL1760/.*\.html)',
				next_step: 'content'
			},
			{
				selector_href_text: u'下一页',
				next_step: 'begin'
			}]
		},
		"content": {
			res: {
				selector_xpath: '/html/body/table/tr[2]/td/font/table',
				keep_html_tags: True,
				next_step: 'db'
			}
		},
		"db": {
			type: "db",
			table_name: "TcmSeedResource",
			fields: [{
				name: "DrugManufacturerID",
				reference: {
					field: "CompanyName",
					table: "TB_Resources_MedicineProductionUnit",
					remote_field: "CompanyName"
				}
			}, {
				name: "PublicationDate",
				selector_table_sibling: u'发布日期',
				data_type: "Date"
			}, {
				name: "Headline",
				selector_css: '.articletitle3'
			}, {
				name: "CompanyName",
				selector_table_sibling: u'企业名称'
			}, {
				name: "CorporateRep",
				selector_table_sibling: u'企业法定代表人'
			}, {
				name: "DrugProductionPermitNumber",
				selector_table_sibling: u'药品生产许可证编号'
			}, {
				name: "SocialCreditNumber",
				selector_table_sibling: u'社会信用代码'
			}, {
				name: "CompanyManInCharge",
				selector_table_sibling: u'企业负责人'
			}, {
				name: "QualityManInCharge",
				selector_table_sibling: u'质量负责人'
			}, {
				name: "ProductionManInCharge",
				selector_table_sibling: u'生产负责人'
			}, {
				name: "QualityAuthorizedPerson",
				selector_table_sibling: u'质量受权人'
			}, {
				name: "ProductionAddress",
				selector_table_sibling: u'生产地址'
			}, {
				name: "InspectionDate",
				selector_table_sibling: u'检查日期'
			}, {
				name: "Inspector",
				selector_table_sibling: u'检查单位'
			}, {
				name: "InspectionReason",
				selector_table_sibling: u'事由'
			}, {
				name: "InspectionResult",
				selector_table_next_row: u'检查发现问题'
			}, {
				name: "FollowUpAction",
				selector_table_next_row: u'处理措施'
			}
			]
		}
	}

class Spider(SpiderWrapper):
	config = ScrapyConfig()

