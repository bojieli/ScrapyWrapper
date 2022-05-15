#/usr/bin/python3
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
import re

def extract_name(name, meta):
    name = re.sub(r'\(.*\)', '', name)
    name = re.sub(r'\[.*\]', '', name)
    name = re.sub(r'\{.*\}', '', name)
    return name.strip()

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
        first_left_bracket = body.find(name + '（')
        if first_left_bracket == -1:
            first_left_bracket = body.find(name + ' （')
            if first_left_bracket == -1:
                return None
    first_left_bracket += len(name) + 1
    first_right_bracket = body[first_left_bracket:].find(')')
    if first_right_bracket == -1:
        first_right_bracket = body[first_left_bracket:].find('）')
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
    save_pages = True
    use_cached_pages = True
    file_basedir = 'university_logos/china-zhwiki'
    begin_urls = ["https://zh.wikipedia.org/zh-hans/%E4%B8%AD%E5%9B%BD%E5%A4%A7%E9%99%86%E9%AB%98%E7%AD%89%E5%AD%A6%E6%A0%A1%E5%88%97%E8%A1%A8"]
    steps = {
        "begin": {
            'res': {
                'selector_xpath': '//a/@href',
                'selector_regex': '(.*/wiki/.*)',
                'next_step': 'university'
            },
        },
        'university': {
           'res': {
                'next_step': 'db'
            }
        },
        "db": {
            'type': "db",
            'table_name': "universities_china_zhwiki",
            'unique': ['name'],
            'upsert': True,
            'print_record': True,
            'fields': [{
                'name': 'name',
                'selector_xpath': '//table[@class="infobox vcard"]//span[@class="nickname"]',
                'data_postprocessor': extract_name,
            }, {
                'name': 'name_zh',
                'selector_xpath': '//h1[@id="firstHeading"]',
                'data_validator': lambda name,_: name.find('大学') != -1 or name.find('学院') != -1,
                'required': True
            }, {
                'name': 'logo',
                'selector_xpath': '//table[@class="infobox vcard"]//img/@src',
                'download_single_url': True
            }, {
                'name': 'domain',
                'selector_xpath': '//table[@class="infobox vcard"]//a[contains(@class, "external")]/@href',
                'data_postprocessor': check_domain,
                'required': True
            }, {
                'name': 'abbreviation',
                'selector_xpath': '//div[@id="bodyContent"]',
                'strip_tags': True,
                'data_postprocessor': extract_abbrev,
                'dependencies': ['name_zh']
            }]
        }
    }

myspider = SpiderFactory(ScrapyConfig(), __name__)

