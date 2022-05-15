#/usr/bin/python3
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
import re

def check_domain(url, meta):
    results = re.match(r'^https?://([a-zA-Z0-9-.]+)', url)
    if not results:
        print('Invalid URL: ' + url)
        return None
    domain = results.group(1)
    results = re.search(r'[a-zA-Z0-9-]+\.edu\.cn$', domain)
    if results:
        return results.group(0)
    if domain.startswith('www.'):
        domain = domain[4:]
    if domain == 'web.archive.org':
        results = re.search(r'web.archive.org/.*/(https?://.*)', url)
        if not results:
            return None
        return check_domain(results.group(1), meta)
    return domain

def extract_abbrev(body, meta):
    name = meta['name']
    body = re.sub(r'[\s]+', ' ', body, 0)
    first_left_bracket = body.find(name + ' (')
    if first_left_bracket == -1:
        return None
    first_left_bracket += len(name) + 1
    first_right_bracket = body[first_left_bracket:].find(')')
    if first_right_bracket == -1:
        return None
    text_in_bracket = body[first_left_bracket + 1:first_left_bracket + first_right_bracket]
    if not text_in_bracket:
        return None
    words = text_in_bracket.split(' ')
    for word in words:
        if len(word) >= 3 and len(word) <= 10 and re.match(r'^[A-Z]+$', word):
            return word
    return None

class ScrapyConfig(ScrapyWrapperConfig):
    file_basedir = 'university_logos/china'
    begin_urls = ["https://en.wikipedia.org/wiki/List_of_universities_in_China"]
    steps = {
        "begin": {
            'res': {
                'selector_xpath': '//a/@href',
                'selector_regex': '(.*/wiki/List_of_universities_and_colleges_in_.*)',
                'next_step': 'province'
            },
        },
        'province': {
            'res': {
                'selector_xpath': '//div[@id="bodyContent"]',
                'next_step': 'province_parse'
            }
        },
        'province_parse': {
            'type': 'intermediate',
            'res': {
                'selector_xpath': '//table[contains(@class, "wikitable")]//tr',
                'next_step': 'province_parse_row'
            }
        },
        'province_parse_row': {
            'type': 'intermediate',
            'fields': [{
                'name': 'name',
                'selector_xpath': '(//td)[1]',
                'required': True
            }, {
                'name': 'name_zh',
                'selector_xpath': '(//td)[2]',
                'required': True
            }],
            'res': {
                'selector_xpath': '(//td)[1]//a/@href',
                'selector_regex': '(.*/wiki/.*)',
                'next_step': 'university'
            }
        },
        'university': {
           'res': {
                'next_step': 'db'
            }
        },
        "db": {
            'type': "db",
            'table_name': "universities_china",
            'unique': ['name'],
            'upsert': True,
            'print_record': True,
            'fields': [{
                'name': 'logo',
                'selector_xpath': '//table[@class="infobox vcard"]//img/@src',
                'download_single_url': True
            }, {
                'name': 'domain',
                'selector_xpath': '//table[@class="infobox vcard"]//th[contains(text(), "Website")]/following-sibling::td//a/@href',
                'data_postprocessor': check_domain
            }, {
                'name': 'abbreviation',
                'selector_xpath': '//div[@id="bodyContent"]',
                'strip_tags': True,
                'data_postprocessor': extract_abbrev,
            }]
        }
    }

myspider = SpiderFactory(ScrapyConfig(), __name__)

