#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
from scrapywrapper.helper import to_pinyin_name

class ScrapyConfig(ScrapyWrapperConfig):
    #use_http_proxy = False
    file_basedir = 'teacher_images/NJUST'
    begin_urls = ["https://gs.njust.edu.cn/dsjs/list.htm"]
    steps = {
        "begin": {
            'res': {
                'selector_xpath': '//a/@href',
                'selector_regex': '(.*DsDir_View.aspx.*)',
                'next_step': 'list'
            },
        },
        'list': {
            'res': {
                'selector_xpath': '//a/@href',
                'selector_regex': '(.*TutorInfo.aspx.*)',
                'next_step': 'profile'
            }
        },
        'profile': {
            'res': {
                'next_step': 'db'
            }
        },
        "db": {
            'type': "db",
            'table_name': "njust_teachers",
            'unique': ['email'],
            'upsert': True,
            'fields': [{
                'name': "email",
                'selector_table_sibling': 'Email',
                'required': True
            }, {
                'name': 'name',
                'selector_table_sibling': '姓 名',
                'required': True
            }, {
                'name': 'name_en',
                'selector_table_sibling': '姓 名',
                'data_postprocessor': lambda name,_: to_pinyin_name(name),
                'required': True
            }, {
                'name': 'org',
                'selector_table_sibling': '所在学院'
            }, {
                'name': 'title',
                'selector_table_sibling': '技术职称',
            }, {
                'name': 'pi_type',
                'selector_table_sibling': '导师类别',
            }, {
                'name': "url",
                'selector_table_sibling': '个人主页',
            }, {
                'name': 'image',
                'selector_xpath': '//img[@id="ctl00_contentParent_imgPhoto"]/@src',
                #'data_validator': lambda url,_: url.startswith('../public/'),
                'download_single_url': True
            }]
        }
    }

myspider = SpiderFactory(ScrapyConfig(), __name__)

