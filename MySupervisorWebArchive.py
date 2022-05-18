#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
import re
from datetime import datetime

def extract_university(text, meta):
    for x in text.split('‹'):
        x = x.strip().replace('_', '')
        if x.find('University') != -1 or x.find('大学') != -1:
            return x
        if x.find('中科院') != -1:
            return '中科院'
    return None

def extract_org(text, meta):
    l = text.split('‹')
    if len(l) <= 3:
        return None
    org = l[-1]
    return org.strip().replace('_', '')

def get_publish_time(text, meta):
    try:
        obj = datetime.strptime(text, '%Y年 %m月 %d日 %H:%M')
        return obj.strftime('%Y-%m-%d %H:%M')
    except Exception as e:
        return text

class ScrapyConfig(ScrapyWrapperConfig):
    begin_urls = ["https://raw.githubusercontent.com/wangzhiye-tiancai/mysupervisor_save/gh_pages/view.json"]
    steps = {
        "begin": {
            'res': {
                'selector_json': '',
                'next_step': 'list'
            },
        },
        'list': {
            'type': 'intermediate',
            'res': {
                'selector_json': 'archiveurl',
                'selector_regex': '(.*web.archive.org.*)',
                'next_step': 'teacher'
            },
            'fields': [{
                'name': 'origin_url',
                'selector_json': 'originurl',
                'required': True
            }, {
                'name': 'archive_time',
                'selector_json': 'time',
                'required': True
            }]
        },
        'teacher': {
            'res': {
                'next_step': 'extract_teacher_info'
            }
        },
        'extract_teacher_info': {
            'type': 'intermediate',
            'res': {
                'selector_xpath': '//div[@id="page-body"]//div[contains(@class, "poster1 post")]',
                'next_step': 'db',
            },
            'fields': [{
                'name': 'teacher',
                'selector_xpath': '//a/span[@style="font-size:2em"]',
                'required': True
            }, {
                'name': 'school_str',
                'selector_xpath': '//div[@class="navbar"]//li[@class="icon-home"]',
                'strip_tags': True,
                'required': True
            }, {
                'name': 'university',
                'selector_xpath': '//div[@class="navbar"]//li[@class="icon-home"]',
                'strip_tags': True,
                'data_postprocessor': extract_university
            }, {
                'name': 'org',
                'selector_xpath': '//div[@class="navbar"]//li[@class="icon-home"]',
                'strip_tags': True,
                'data_postprocessor': extract_org
            }]
        },
        "db": {
            'type': "db",
            'table_name': "mysupervisor_reviews",
            'unique': ['postid'],
            'upsert': True,
            'fields': [{
                'name': 'postid',
                'selector_regex': '<div id="(p[0-9]+)"',
                'data_postprocessor': lambda x,_: x[1:],
                'required': True
            }, {
                'name': 'rating_academic',
                'selector_xpath': '(//tr[@class="rating_item"])[1]',
                'required': True
            }, {
                'name': 'rating_financial',
                'selector_xpath': '(//tr[@class="rating_item"])[2]',
                'required': True
            }, {
                'name': 'rating_relationship',
                'selector_xpath': '(//tr[@class="rating_item"])[3]',
                'required': True
            }, {
                'name': 'rating_prospect',
                'selector_xpath': '(//tr[@class="rating_item"])[4]',
                'required': True
            }, {
                'name': 'content',
                'selector_xpath': '//div[@class="content"]',
                'required': True
            }, {
                'name': 'author',
                'selector_xpath': '(//dl[@class="postprofile"]/dt)[1]',
                'strip_tags': True,
                'required': True
            }, {
                'name': 'publish_time',
                'selector_xpath': '(//dl[@class="postprofile"]/dt)[2]',
                'strip_tags': True,
                'data_postprocessor': get_publish_time,
                'required': True
           }]
        }
    }

myspider = SpiderFactory(ScrapyConfig(), __name__)

