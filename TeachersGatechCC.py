#/usr/bin/python3
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
import re

def find_email(text, suffix):
    match = re.search(r'[a-zA-Z0-9_-]+@[a-zA-Z0-9_.-]+', text)
    if not match:
        return None
    return match.group(0)

def find_homepage(text):
    match = re.search(r'http[s]*://[a-zA-Z0-9_./~-]+', text)
    if not match:
        return None
    return match.group(0)

class ScrapyConfig(ScrapyWrapperConfig):
    file_basedir = 'teacher_images/gatech_cc'
    begin_urls = [ "https://www.cc.gatech.edu/people/faculty?page=" + str(i) for i in range(0, 25) ]
    steps = {
        "begin": {
            'res': {
                'selector_xpath': '//a/@href',
                'data_validator': lambda url,_ : url.startswith('/people/') and not url.startswith('/people/faculty'),
                'next_step': 'page',
            }
        },
        "page": {
            'res': {
                'next_step': 'db',
            }
        },
        "db": {
            'type': "db",
            'table_name': "gatech_cc_teachers",
            'unique': ['email'],
            'upsert': True,
            'print_record': True,
            'fields': [{
                'name': 'name',
                'selector_xpath': '//h1[@class="page-title"]',
                'strip_tags': True,
                'required': True
            }, {
                'name': 'email',
                'selector_xpath': '//div[contains(@class, "profile-card__content")]',
                'data_postprocessor': lambda text,_: find_email(text, 'gatech.edu'),
                'strip_tags': True,
                'required': True
            }, {
                'name': 'title',
                'selector_xpath': '//h6[contains(@class, "card-block__subtitle")]',
                'strip_tags': True,
                'required': True
            }, {
                'name': 'image',
                'selector_xpath': '//div[contains(@class, "profile-card__content")]//img/@src',
                'download_single_url': True
            }, {
                'name': 'url',
                'selector_css': '.card-block',
                'data_postprocessor': lambda text,_: find_homepage(text),
                'strip_tags': True
            }]
        }
    }

myspider = SpiderFactory(ScrapyConfig(), __name__)
