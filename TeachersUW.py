#/usr/bin/python3
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
import re

def split_faculty_cards(html, meta):
    cards = html.decode('utf-8').split('<h4>')
    return [ '<h4>' + card for card in cards[1:] ]

class ScrapyConfig(ScrapyWrapperConfig):
    file_basedir = 'teacher_images/uw'
    begin_urls = ["https://www.washington.edu/about/academics/departments/"]
    steps = {
        "begin": {
            'res': {
                'selector_xpath': '//div[@id="main_content"]//li',
                'strip_tags': True,
                'next_step': 'record_org',
                'required': True
            }
        },
        'record_org': {
            'type': 'intermediate',
            'res': {
                'next_step': 'search_faculty'
            },
            'fields': [{
                'name': 'org',
                'required': True
            }]
        },
        'search_faculty': {
            'req': {
                'method': 'post',
                'url': 'https://directory.uw.edu/',
                'post_formdata': {
                    'query': lambda text, meta: text,
                    'method': 'department',
                    'population': 'employees',
                    'length': 'full'
                }
            },
            'res': {
                'selector': split_faculty_cards,
                'next_step': 'db'
            }
        },
        "db": {
            'type': "db",
            'table_name': "uw_teachers",
            'unique': ['email'],
            'upsert': True,
            'print_record': True,
            'fields': [{
                'name': 'name',
                'selector_xpath': '//h4',
                'strip_tags': True,
                'required': True
            }, {
                'name': 'email',
                'selector_xpath': '//ul[@class="dir-listing"]/li',
                'strip_tags': True,
                'required': True
            }, {
                'name': 'title',
                'selector_xpath': '//ul[@class="multiaddr"]/li',
                'strip_tags': True,
                'data_postprocessor': lambda text,meta: text.split(',')[0].strip()
            }, {
                'name': 'intro',
                'selector_xpath': '//ul[@class="multiaddr"]',
                'data_postprocessor': lambda text,meta: text.replace('<li>', '').replace('</li>', '\n')
            }]
        }
    }

myspider = SpiderFactory(ScrapyConfig(), __name__)

#import sys
#if len(sys.argv) == 2:
#    print(is_human_face(sys.argv[1]))
