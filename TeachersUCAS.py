#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
from scrapywrapper.helper import to_pinyin_name
import re

def extract_email(text, meta):
    needle = '电子邮件：'
    pos = text.find(needle)
    if pos == -1:
        print('Email not found in: ' + text[:200])
        return None
    email = text[pos + len(needle):].strip()
    info = re.match(r'[a-zA-Z0-9-_.]+@[a-zA-Z0-9-_.]+', email)
    if not info:
        print('Invalid email ' + email[:200])
        return None
    return info.group(0)

def extract_info(text, meta, offset, field):
    pos = text.find('电子邮件')
    if pos != -1:
        text = text[:pos]
    text = text.replace('&nbsp;', ' ')
    text = re.sub('[\s]+', ' ', text)
    info = text.split(' ')
    if len(info) < 4:
        if len(info) == 3:
            if field == 'org' and info[offset].find('研究所') != -1:
                return info[offset]
            if field == 'title' and info[offset].find('研究所') == -1 and info[offset] != '男' and info[offset] != '女':
                return info[offset]
        print('Invalid info: ' + text[:200])
        return None
    return info[offset]

def extract_org(text, meta):
    return extract_info(text, meta, -1, 'org')

def extract_title(text, meta):
    return extract_info(text, meta, -2, 'title')

def extract_original_info(text, meta):
    pos = text.find('电子邮件')
    if pos != -1:
        text = text[:pos]
    return text

class ScrapyConfig(ScrapyWrapperConfig):
    save_pages = True
    use_cached_pages = True
    file_basedir = 'teacher_images/UCAS'
    begin_urls = ["https://www.ucas.ac.cn/site/77"]
    steps = {
        "begin": {
            'res': {
                'selector_xpath': '//a',
                'next_step': 'extract_url'
            }
        },
        'extract_url': {
            'type': 'intermediate',
            'res': {
                'selector_xpath': '//a/@href',
                'selector_regex': '(http://people.ucas.ac.cn/.*)',
                'data_postprocessor': lambda url,_: url.replace('http://', 'https://'),
                'next_step': 'teacher'
            },
            'fields': [{
                'name': 'name',
                'selector_xpath': '//a/@fullname',
                'required': True
            }, {
                'name': 'url',
                'selector_xpath': '//a/@href',
                'selector_regex': '(http://people.ucas.ac.cn/.*)',
                'data_postprocessor': lambda url,_: url.replace('http://', 'https://'),
                'required': True
            }]
        },
        'teacher': {
            'res': {
                'next_step': 'db'
            }
        },
        "db": {
            'type': "db",
            'table_name': "ucas_teachers",
            'unique': ['email'],
            'upsert': True,
            'fields': [{
                'name': "email",
                'selector_xpath': '//div[@class="bp-enty"]',
                'strip_tags': True,
                'data_postprocessor': extract_email,
                'required': True
            }, {
                'name': 'org',
                'selector_xpath': '//div[@class="bp-enty"]//b|//div[@class="bp-enty"]//strong',
                'strip_tags': True,
                'data_postprocessor': extract_org,
            }, {
                'name': 'title',
                'selector_xpath': '//div[@class="bp-enty"]//b|//div[@class="bp-enty"]//strong',
                'strip_tags': True,
                'data_postprocessor': extract_title,
            }, {
                'name': 'original_info',
                'selector_xpath': '//div[@class="bp-enty"]//b|//div[@class="bp-enty"]//strong',
                'strip_tags': True,
                'data_postprocessor': extract_original_info,
            }, {
                'name': 'image',
                'selector_xpath': '//div[@class="b-pinfo"]//img[@class="bp-photo"]/@src',
                'data_validator': lambda url, _: url.find('tx.jpg/url') == -1,
                'download_single_url': True
            }, {
                'name': 'name_en',
                'data_postprocessor': lambda info, meta: to_pinyin_name(meta['name']),
                'required': True
            }]
        }
    }

myspider = SpiderFactory(ScrapyConfig(), __name__)

