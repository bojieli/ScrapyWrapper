#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig

class ScrapyConfig(ScrapyWrapperConfig):
    #use_http_proxy = False
    begin_urls = ["https://www.professoren.tum.de/en/professors/alphabetical"]
    steps = {
        "begin": {
            'res': {
                'selector_css': 'div.content__main',
                'next_step': 'list'
            },
        },
        'list': {
            'type': 'intermediate',
            'res': {
                'selector_xpath': '//a/@href',
                'selector_regex': '(/en/.*)',
                'next_step': 'profile'
            }
        },
        'profile': {
            'res': {
                'selector_xpath': '//body',
                'next_step': 'profile_parse'
            }
        },
        "profile_parse": {
            'type': 'intermediate',
            "fields": [{
                'name': 'name',
                'selector_xpath': '//li[@class="breadcrumb__item breadcrumb__item--last"]/a',
                'required': True
            }, {
                'name': 'org',
                'selector_xpath': '//h3[contains(text(), "Department")]/../p/a'
            }, {
                'name': 'professorship',
                'selector_xpath': '//h3[contains(string, "Professorship")]/../p/a'
            }, {
                'name': 'title',
                'selector_xpath': '//h1[@id="first"]',
                'required': True
            }, {
                'name': 'image',
                'selector_xpath': '//div[@class="professor__single--image"]/img/@src'
            }],
            'res': {
                'selector_xpath': '//h3[contains(text(), "Contact Details")]/../p/a/@href',
                'selector_regex': '(.*)',
                'next_step': 'contact'
            }
        },
        "contact": {
            'res': {
                'selector_xpath': '//body',
                'next_step': 'db'
            }
        },
        "db": {
            'type': "db",
            'table_name': "tum_teachers",
            'unique': ['email'],
            'upsert': True,
            'fields': [{
                'name': "email",
                'selector_table_sibling': 'E-Mail',
                'data_postprocessor': lambda email,_: email.replace('(at)', '@'),
                'required': True
            }, {
                'name': "url",
                'selector_table_sibling': 'Homepage'
            }]
        }
    }

myspider = SpiderFactory(ScrapyConfig(), __name__)

