#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
import re
import json
import demjson
import urllib

# 对统计列表页返回的 JSON 做处理，记录内部 ID 的对应关系
# 这里 meta 是按引用传递的解析过程元数据。用 $$ 开头是为了不让它入库
def get_code_mapping(text, meta):
	obj = demjson.decode(text)
	mapping = {}
	try:
		for zb in obj['returndata']['wdnodes'][0]['nodes']:
			mapping[zb['code']] = zb
		meta['$$mapping_code_to_zb'] = mapping
	except:
		print(obj)
	return text

# 爬虫配置主入口
class ScrapyConfig(ScrapyWrapperConfig):
    # 爬虫抓取的起始链接，可以是一个 list，也可以是一个 generator
	begin_urls = ['A0O']
    # 爬虫分为若干 steps（步骤），组织成一个 dict，第一步固定为 "begin"。解析过程是一个状态机。
	steps = {
        # 第一步固定为 begin
        # 第一步，调用 JSON API 获取健康信息目录
		"begin": {
            # 构造 HTTP POST 请求
			'req': {
				'url': 'http://data.stats.gov.cn/easyquery.htm',
				'method': 'post',
				'post_formdata': {
                    # 这里的 lambda 可以接受两个参数：url 和 meta，这里只使用了 url
					'id': lambda url,_: url,
					'dbcode': 'hgnd',
					'wdcode': 'zb',
					'm': 'getTree'
				}
			},
            # 返回的 JSON 列表每一项都是一个 classification，直接展开
			'res': {
                # 匹配结果中的每一项都会 fork 出一个下一阶段
				'selector_json': '',
				'next_step': 'content'
			}
		},
        # 第二步，把分类信息入库
		"content": {
            # type: db 表示是数据库阶段。
			'type': 'db',
            # 数据库表名
			'table_name': 'AnnualHealthStasticClassification',
            # 数据库判断是否重复的索引字段集合
			'unique': ['HealthPath'],
            # 如果发现数据库中已有数据，是否更新（True 表示更新，False 表示不更新）
			'upsert': True,
            # fields 表示解析出来的数据字段
			'fields': [{
				'name': 'HealthName',
                # selector_json 表示获取 json 中名为 name 的项
				'selector_json': 'name',
				'required': True
			}, {
				'name': 'HealthPath',
				'selector_json': 'id',
				'required': True
			}],
            # 继续解析，进入下一级列表或者详情页
            # 需要注意，fields 的解析是根据上一阶段传来的信息，在当前阶段发送 HTTP 请求之前，不要与 res 弄混了。res 是解析当前阶段 HTTP 请求的结果。
			'res': [
			{
				'selector_json': 'isParent',
                # 如果 isParent 是 true，说明还有下级列表，返回 begin 继续遍历下级列表
				'data_validator': lambda m,_: m == 'true',
                # 此处是把当前阶段 fields 过程中解析出来的 HealthPath 传到 begin 阶段，以便获取子目录
				'data_postprocessor': lambda _,meta: meta['HealthPath'],
				'next_step': 'begin'
			},
			{
                # 进入获取详情信息阶段
				'selector_json': 'id',
				'next_step': 'rows'
			} 
			]
		},
        # 第三步，获取详情信息表格
		"rows": {
            # 构造 HTTP POST 请求
			'req': {
				'method': 'post',
                # 上一步传来的是 id，需要构造出请求
                # LAST20 表示获取 20 年以来（最多）的信息
				'url': lambda _id, meta: 'http://data.stats.gov.cn/easyquery.htm?m=QueryData&dbcode=hgnd&rowcode=zb&colcode=sj&wds=%5B%5D&dfwds=' + urllib.quote('[{"wdcode":"zb","valuecode":"' + _id + '"},{"wdcode":"sj","valuecode":"LAST20"}]')
			},
			'res': {
                # 对返回的 JSON 做预处理，内部 ID 映射信息保存在 meta 里面
				'data_preprocessor': get_code_mapping,
                # 获取表中每一行的信息，入库
				'selector_json': 'returndata.datanodes',
				'next_step': 'db'
			},
		},
        # 第四步，入库
		"db": {
			'type': "db",
			'unique': ['HealthDataTypeID', 'StatisticType', 'DataYear'],
			'upsert': True,
			'table_name': "AnnualHealthStastic",
			'fields': [{
                # HealthName 数据库中不存在，删除
				'name': 'HealthName', 'value': None
			}, {
                # HealthPath 数据库中不存在，删除
				'name': 'HealthPath', 'value': None
			}, {
				'name': 'HealthDataTypeID',
                # meta['$$info_id'] 是上次插入数据库的 ID 号，用于在父表和子表间建立关联。父表 Classification 在前面的阶段已经入库，把其 ID 传给后面的阶段以便建立关联。
				'selector': lambda _,meta: meta['$$info_id']
			}, {
                # 根据上一阶段建立的映射，获取统计类型
				'name': 'StatisticType',
                # 获取 JSON 中 .wds[0].valuecode 域
				'selector_json': 'wds.0.valuecode',
				'data_postprocessor': lambda code, meta: meta['$$mapping_code_to_zb'][code]['cname'],
				'required': True
			}, {
                # 根据上一阶段建立的映射，获取统计单位
				'name': 'StatisticUnit',
				'selector_json': 'wds.0.valuecode',
				'data_postprocessor': lambda code, meta: meta['$$mapping_code_to_zb'][code]['unit'],
				'required': True
			}, {
                # 根据上一阶段建立的映射，获取统计备注
				'name': 'StatisticTypeComment',
				'selector_json': 'wds.0.valuecode',
				'data_postprocessor': lambda code, meta: meta['$$mapping_code_to_zb'][code]['exp']
			}, {
				'name': 'DataYear',
				'selector_json': 'wds.1.valuecode',
                # 解析为整数，如发现不是整数则报错，不插入此条数据
				'data_type': 'int',
				'required': True
			}, {
				'name': 'AffectedPopulation',
				'selector_json': 'data.data',
                # 解析为浮点数，如发现不是整数则报错，不插入此条数据
				'data_type': 'float',
				'required': True
			}]
		}
	}

myspider = SpiderFactory(ScrapyConfig(), __name__)

