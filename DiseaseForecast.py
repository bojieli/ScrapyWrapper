#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig

# 根据上一目录页面 URL 生成下一目录页面 URL
def get_next_url(url):
	pattern = "xxgkml_1_4443"
	pos = url.find(pattern) + len(pattern)
	prefix = url[:pos]
	suffix = url[pos:]
	if suffix == '.htm':
		return prefix + '_1.htm'
	else:
		pagenum = int(suffix[1:-4]) + 1
		return prefix + '_' + str(pagenum) + '.htm'

# 爬虫配置主入口
class ScrapyConfig(ScrapyWrapperConfig):
    # 爬虫抓取的起始链接，可以是一个 list，也可以是一个 generator
	begin_urls = ["http://www.aqsiq.gov.cn/xxgk_13386/tsxx/yqts/xxgkml_1_4443.htm"]
    # 爬虫分为若干 steps（步骤），组织成一个 dict，第一步固定为 "begin"。解析过程是一个状态机。
	steps = {
        # 第一步固定为 begin
        # 第一步，获取目录页
		"begin": {
            # res 表示获取到内容之后如何处理。是一个 list，list 中的每个元素是并行处理。
            # 第一个处理逻辑是找到页面中的链接，进入详情页面
			'res': [{
                # selector_regex 匹配正则表达式，获取第一个括号（capture group）中内容
				'selector_regex': 'href="(\./[^"]*)"',
                # next_step 是下一阶段的名字
				'next_step': 'content'
			},
            # 第二个处理逻辑是找到“下一页”这几个字对应的链接，进入下一目录页面。目录页面的处理是递归的，因此回到 begin 阶段自己。
            # 其中下一页面的链接用 get_next_url 函数生成。
			{
				'selector_regex': u'(下一页)',
                # data_postprocessor 表示数据后处理，参数：匹配结果 result，元数据 meta。元数据 meta 贯穿整个数据解析过程。
                # meta['$$url'] 是一个自动生成的元数据，表示当前 url
				'data_postprocessor': lambda _, meta: get_next_url(meta['$$url']),
				'next_step': 'begin'
			}]
		},
        # 第二步，获取详情页
		"content": {
			'res': {
                # 根据 css 匹配 div.yy 的内容，传递给下一步
				'selector_css': 'div.yy',
				'next_step': 'db'
			}
		},
        # 第三步，入库
		"db": {
            # type: db 表示是数据库阶段。
			'type': "db",
            # 数据库表名
			'table_name': "DiseaseForecast",
            # 数据库判断是否重复的索引字段集合
			'unique': ['PublicationDate', 'Headline'],
            # 如果发现数据库中已有数据，是否更新（True 表示更新，False 表示不更新）
			'upsert': True,
            # fields 表示解析出来的数据字段。与 res 的匹配结构类似。
			'fields': [{
                # 字段名
				'name': "PublicationDate",
                # 匹配选择器，选择器种类包括 selector_regex, selector_css, selector_xpath, selector_json
				'selector_regex': u'发布时间：([0-9-]*)',
                # 数据类型，默认为 raw 字符串。可以灵活解析为 Date，int，float 三种类型。
				'data_type': "Date",
				# 是否必须，如果必须字段为空，会不插入此条数据，并记录错误日志
                'required': True
			}, {
				'name': "Headline",
				'selector_css': 'h1',
				'required': True
			}, {
				'name': "DetailContent",
				'selector_css': 'div.TRS_Editor',
				'required': True,
                # 如果需要保留匹配结果中的 HTML 标签，设置 strip_tags。默认自动去除 HTML 标签。
				'strip_tags': False
			}]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

