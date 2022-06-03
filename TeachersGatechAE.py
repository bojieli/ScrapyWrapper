#/usr/bin/python3
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig

class ScrapyConfig(ScrapyWrapperConfig):
    file_basedir = 'teacher_images/gatech_ae'
    begin_urls = ["https://ae.gatech.edu/people"]
    steps = {
        "begin": {
            'res': {
                'selector_xpath': '//a/@href',
                'data_validator': lambda url,_ : url.startswith('/people/'),
                'next_step': 'page',
                'required': True
            }
        },
        "page": {
            'res': {
                'next_step': 'db',
            }
        },
        "db": {
            'type': "db",
            'table_name': "gatech_ae_teachers",
            'unique': ['email'],
            'upsert': True,
            'print_record': True,
            'fields': [{
                'name': 'name',
                'selector_css': '.views-field-field-last-name',
                'strip_tags': True,
                'required': True
            }, {
                'name': 'email',
                'selector_xpath': '//div[contains(@class, "views-field-field-email")]//a/@href',
                'data_postprocessor': lambda text,_: text.replace('mailto:', ''),
                'strip_tags': True,
                'required': True
            }, {
                'name': 'title',
                'selector_css': '.views-field-field-job-title',
                'strip_tags': True,
                'required': True
            }, {
                'name': 'image',
                'selector_xpath': '//div[contains(@class, "views-field-field-headshot")]//img/@src',
                'download_single_url': True
            }]
        }
    }

myspider = SpiderFactory(ScrapyConfig(), __name__)
