#/usr/bin/python3
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig

class ScrapyConfig(ScrapyWrapperConfig):
    file_basedir = 'teacher_images/MIT_EECS'
    begin_urls = ["https://www.eecs.mit.edu/role/faculty/"]
    steps = {
        "begin": {
            'res': {
                'selector_css': '.people-entry',
                'next_step': 'db',
                'required': True
            }
        },
        "db": {
            'type': "db",
            'table_name': "mit_eecs_teachers",
            'unique': ['email'],
            'upsert': True,
            'print_record': True,
            'fields': [{
                'name': 'name',
                'selector_css': 'h5',
                'strip_tags': True,
                'required': True
            }, {
                'name': 'email',
                'selector_regex': r'([a-zA-Z0-9_-]+@[a-zA-Z0-9_.-]+)',
                'required': True
            }, {
                'name': 'title',
                'selector_css': 'p',
                'strip_tags': True,
                'required': True
            }, {
                'name': 'image',
                'selector_xpath': '//a[@class="people-index-image"]/img/@src',
                'download_single_url': True,
                'required': True
            }, {
                'name': 'url',
                'selector_xpath': '//h5/a/@href',
                'required': True
            }]
        }
    }

myspider = SpiderFactory(ScrapyConfig(), __name__)
