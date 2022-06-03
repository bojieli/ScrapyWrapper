#/usr/bin/python3
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig

class ScrapyConfig(ScrapyWrapperConfig):
    file_basedir = 'teacher_images/gatech'
    begin_urls = ["https://www.ece.gatech.edu/faculty-staff-directory"]
    steps = {
        "begin": {
            'res': {
                'selector_css': '.col-md-4',
                'next_step': 'db',
                'required': True
            }
        },
        "db": {
            'type': "db",
            'table_name': "gatech_teachers",
            'unique': ['email'],
            'upsert': True,
            'print_record': True,
            'fields': [{
                'name': 'name',
                'selector_css': '.field-full-name',
                'strip_tags': True,
                'required': True
            }, {
                'name': 'email',
                'selector_xpath': '//div[@class="field-email-address"]/a/@href',
                'data_postprocessor': lambda text,_: text.replace('mailto:', ''),
                'strip_tags': True,
                'required': True
            }, {
                'name': 'title',
                'selector_css': '.field-jobtitle',
                'strip_tags': True,
                'required': True
            }, {
                'name': 'image',
                'selector_xpath': '//div[@class="faculty-staff-image"]/img/@src',
                'data_validator': lambda url,_: url.find('default_images/') == -1,
                'download_single_url': True
            }]
        }
    }

myspider = SpiderFactory(ScrapyConfig(), __name__)
