#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig

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


# debug 共有四个调试信息打印点：
#### req（HTTP 请求与响应）
#### res（内容匹配结果）
#### field（解析字段结果）
#### db（数据库记录）

class ScrapyConfig(ScrapyWrapperConfig):
    begin_urls = ["http://www.aqsiq.gov.cn/xxgk_13386/tsxx/yqts/xxgkml_1_4443.htm"]
    steps = {
        "begin": {
            # debug 表示把请求的 request 和 response 信息打印出来
            'req': {'debug': True},
            'res': [{
                'selector_regex': 'href="(\./[^"]*)"',
                'next_step': 'content',
                # debug 表示把 res 的匹配结果打印出来
                'debug': True
            },
            {
                'selector_regex': u'(下一页)',
                'data_postprocessor': lambda _, meta: get_next_url(meta['$$url']),
                'next_step': 'begin',
                # debug 表示把 res 的匹配结果打印出来
                'debug': True
            }]
        },
        "content": {
            # debug 表示把请求的 request 和 response 信息打印出来
            'req': {'debug': True},
            'res': {
                'selector_css': 'div.yy',
                'next_step': 'db',
                # debug 表示把 res 的匹配结果打印出来
                'debug': True
            }
        },
        "db": {
            'type': "db",
            'table_name': "DiseaseForecast",
            'unique': ['PublicationDate', 'Headline'],
            'upsert': True,
            # debug 表示把插入数据库的记录打印出来
            'debug': True,
            'fields': [{
                'name': "PublicationDate",
                'selector_regex': u'发布时间：([0-9-]*)',
                'data_type': "Date",
                'required': True,
                # debug 表示把 field 的匹配结果打印出来
                'debug': True
            }, {
                'name': "Headline",
                'selector_css': 'h1',
                'required': True,
                # debug 表示把 field 的匹配结果打印出来
                'debug': True
            }, {
                'name': "DetailContent",
                'selector_css': 'div.TRS_Editor',
                'required': True,
                'strip_tags': False,
                # debug 表示把 field 的匹配结果打印出来
                'debug': True
            }]
        }
    }

myspider = SpiderFactory(ScrapyConfig(), __name__)

