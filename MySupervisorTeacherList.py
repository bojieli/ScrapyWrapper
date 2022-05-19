#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
import re
from datetime import datetime

def extract_university(text, meta):
    for x in text.split('<'):
        x = x.strip().replace('_', '')
        if x.find('University') != -1 or x.find('大学') != -1:
            return x
        if x.find('中科院') != -1:
            return '中科院'
    return None

def extract_org(text, meta):
    l = text.split('<')
    if len(l) <= 3:
        return None
    org = l[-1]
    return org.strip().replace('_', '')

class ScrapyConfig(ScrapyWrapperConfig):
    begin_urls = ["https://mysupervisor.org/"]
    steps = {
        "begin": {
            'res': [{
                'selector_xpath': '//div[contains(@class, "departments")]//a/@href',
                'next_step': 'begin'
            }, {
                'next_step': 'extract_info',
            }]
        },
        'extract_info': {
            'type': 'intermediate',
            'res': {
                'selector_xpath': '//div[contains(@class, "profs")]//div[contains(@class, "prof-name")]',
                'next_step': 'db',
            },
            'fields': [{
                'name': 'school_str',
                'selector_xpath': '//div[@id="nav-links"]',
                'strip_tags': True,
                'required': True
            }, {
                'name': 'university',
                'selector_xpath': '//div[@id="nav-links"]',
                'strip_tags': True,
                'data_postprocessor': extract_university
            }, {
                'name': 'org',
                'selector_xpath': '//div[@id="nav-links"]',
                'strip_tags': True,
                'data_postprocessor': extract_org
            }]
        },
        "db": {
            'type': "db",
            'table_name': "mysupervisor_teachers",
            'unique': ['teacher_id'],
            'upsert': True,
            'fields': [{
                'name': 'teacher_id',
                'selector_regex': '/Topic/View/([0-9]+)',
                'required': True
            }, {
                'name': 'name',
                'selector_xpath': '//a',
                'strip_tags': True,
                'data_postprocessor': lambda name,_: name.replace(' ', ''),
                'required': True
           }]
        }
    }

myspider = SpiderFactory(ScrapyConfig(), __name__)

