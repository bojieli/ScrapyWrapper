#/usr/bin/python3
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
import re
import lxml.html

def check_domain(url, meta):
    results = re.match(r'^https?://([a-zA-Z0-9.]+)', url)
    if not results:
        print('Invalid URL: ' + url)
        return None
    domain = results.group(1)
    results = re.search(r'[a-zA-Z0-9]+\.edu$', domain)
    if results:
        return results.group(0)
    results = re.search(r'[a-zA-Z0-9]+\.edu\.[a-z]+$', domain)
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

def extract_wiki_body(content, meta):
    html = lxml.html.document_fromstring(content)
    for nav in html.xpath('//div[@role="navigation"]'):
        nav.getparent().remove(nav)
    return lxml.etree.tostring(html, method='html', encoding='unicode')


class ScrapyConfig(ScrapyWrapperConfig):
    file_basedir = 'university_logos/global_new'
    begin_urls = ["https://en.wikipedia.org/wiki/Lists_of_universities_and_colleges_by_country"]
    steps = {
        "begin": {
            'res': {
                'selector_xpath': '//div[@id="bodyContent"]//li',
                'next_step': 'region_list'
            },
        },
        'region_list': {
            'type': 'intermediate',
            'fields': [{
                'name': 'region',
                'selector_xpath': '//a',
                'data_validator': lambda region,_: region.find('List of') == -1,
                'required': True
            }],
            'res': {
                'selector_xpath': '//a/@href',
                'selector_regex': '(.*/wiki/List_of.*)',
                'next_step': 'region'
            }
        },
        'region': {
            'res': {
                'selector_xpath': '//li/a/@href',
                'selector_regex': '(.*/wiki/.*)',
                'data_validator': lambda url,_: url.find('Template:') == -1 and url.find('Category:') == -1,
                'next_step': 'university'
            }
        },
        'university': {
            'res': {
                'selector_xpath': '//div[@id="content"]',
                'data_postprocessor': extract_wiki_body,
                'next_step': 'db'
            }
        },
        "db": {
            'type': "db",
            'table_name': "universities_global_new",
            'unique': ['name'],
            'upsert': True,
            'print_record': True,
            'fields': [{
                'name': 'name',
                'selector_xpath': '//h1[@id="firstHeading"]',
                'data_validator': lambda name,_: name.find('List of') == -1 and name.find('Template') == -1 and name.find('Category') == -1,
                'required': True
            }, {
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
                'dependencies': ['name']
            }]
        }
    }

myspider = SpiderFactory(ScrapyConfig(), __name__)

