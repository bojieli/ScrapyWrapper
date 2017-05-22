#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig

# 从股票代码拼接成 URL
def enumerate_first_node_type(url, meta):
	map_category = [u'全部', u'重大事项', u'财务报告', u'融资公告', u'风险提示', u'资产重组', u'信息变更', u'持股变动']
	for i in range(0,8):
		meta['ReportType'] = map_category[i]
		yield {
			'url': 'http://data.eastmoney.com/notices/getdata.ashx?StockCode=' + str(url) + '&CodeType=1&PageIndex=1&PageSize=1000&jsObj=wTHYgfuw&SecNodeType=0&FirstNodeType=' + str(i) + '&rt=49484645' 
		}

# 爬虫配置主入口
class ScrapyConfig(ScrapyWrapperConfig):
    # scrapy 抓取的个性化配置，详情参见 scrapy 文档。这里只是为了示例，没有设置的必要
	custom_settings = {
		'DOWNLOAD_DELAY': 0,
		'CONCURRENT_REQUESTS': 4,
	}

    # 爬虫抓取的起始链接，可以是一个 list，也可以是一个 generator
	begin_urls = ["http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=C.BK04651&sty=FCOIATA&sortType=C&sortRule=-1&page=1&pageSize=1000&js=var%20quote_123%3d{rank:[(x)],pages:(pc)}&token=7bc05d0d4c3c22ef9fca8c2a912d779c&jsName=quote_123&_g=0.0603660640467345"]

    # 爬虫分为若干 steps（步骤），组织成一个 dict，第一步固定为 "begin"。解析过程是一个状态机。
	steps = {
        # 第一步固定为 begin
        # 第一步，获取公司名字列表 json
		"begin": {
			'res': {
                # 这里的 parser: js-object 表示是作为 JSON 解析，默认作为 HTML 解析
			    'parser': 'js-object',
                # selector_json 选择名为 rank 的子元素，如有多个，每个都 fork 出一个新的下一步实例
                # 在这里，每个公司都有一个名为 rank 的，所以选出了所有上市公司
				'selector_json': 'rank',
                # 选择出来的结果取出逗号后的内容，六位股票代码
				'selector': lambda s, meta: s.split(',')[1],
				'next_step': 'list'
			}
		},
        # 第二步，获取上市公司财报目录页
		"list": {
            # 从第一步传过来的股票代码，拼接成一个 URL
			'req': enumerate_first_node_type,
            # 返回的仍然是一个 JSON
			'res': {
			    'parser': 'js-object',
                # 每条财报数据都在这里被解析出来，发给下一步
				'selector_json': 'data',
				'next_step': 'list_parse'
			},
            # 把上一阶段传来的股票代码存进解析过程元数据
            # 需要注意，fields 的解析是根据上一阶段传来的信息，在当前阶段发送 HTTP 请求之前，不要与 res 弄混了。res 是解析当前阶段 HTTP 请求的结果。
			'fields': [{
				'name': '$$StockCode'
			}]
		},
        # 第三步，获取财报的元数据（财报详情页里没有，需要在目录页里解析出来）
		"list_parse": {
            # intermediate type 表示中间阶段，既不发 HTTP，也不入库
            # 共有三种阶段，http（默认），intermediate，db
			'type': 'intermediate',
            # 解析 ReportType2, ReportDate 两个字段
            # （财报详情页里没有，需要在目录页里解析出来）
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
            # 根据 INFOCODE 获取财报详情信息
			'res': {
				'selector_json': 'INFOCODE',
				'next_step': 'content',
				'required': True
			},
		},
        # 第四步，获取财报详情信息页
		"content": {
            # 根据 INFOCODE 拼接出详情页 URL
			'req': {
				'url': lambda url, meta: 'http://data.eastmoney.com/notices/detail/' + meta['$$StockCode'] + '/' + url + ',JUU1JTg1JUI0JUU5JUJEJTkwJUU3JTlDJUJDJUU4JThEJUFG.html'
			},
            # 取出详情页内容
			'res': {
				'selector_css': 'div.content',
				'next_step': 'db',
				'required': True
			},
		},
        # 第五步，入库
		"db": {
            # type: db 表示是数据库阶段。
			'type': "db",
            # 数据库表名
			'table_name': "PublicCompanyReport",
            # 数据库判断是否重复的索引字段集合
			'unique': ['CompanyID', 'PdfUrl'],
            # 如果发现数据库中已有数据，是否更新（True 表示更新，False 表示不更新）
			'upsert': True,
            # fields 表示解析出来的数据字段
            # 注意： $$ 开头的字段在入库的时候都将被删除，也就是 $$ 开头的字段用于保存解析过程中的临时信息
			'fields': [{
                # 字段名
				'name': 'CompanyID',
                # 引用类型
				'reference': {
                    # 引用表名
					'table': 'PublicCompanyInfo',
                    # 解析结果中的关联字段
					'field': '$$StockCode',
                    # 引用表中的关联字段
					'remote_field': 'StockCode'
				},
				# 是否必须，如果必须字段为空，会不插入此条数据，并记录错误日志
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
                # 如果需要保留匹配结果中的 HTML 标签，设置 strip_tags。默认自动去除 HTML 标签。
				'strip_tags': False,
                # 是否下载内文中的图片。strip_tags 为 True 时默认也为 True
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
