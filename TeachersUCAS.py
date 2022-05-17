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

def extract_info(text, meta, offset):
    pos = text.find('电子邮件')
    if pos != -1:
        text = text[:pos]
    text = text.replace('&nbsp;', ' ')
    text = re.sub('[\s]+', ' ', text)
    info = text.split(' ')
    if len(info) < 4:
        print('Invalid info: ' + text[:200])
        return None
    return info[offset]

def extract_org(text, meta):
    return extract_info(text, meta, -1)

def extract_title(text, meta):
    return extract_info(text, meta, -2)

class ScrapyConfig(ScrapyWrapperConfig):
    save_pages = True
    use_saved_pages = True
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
                'next_step': 'teacher'
            },
            'fields': [{
                'name': 'name',
                'selector_xpath': '//a/@fullname',
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
                'required': True
            }, {
                'name': 'title',
                'selector_xpath': '//div[@class="bp-enty"]//b|//div[@class="bp-enty"]//strong',
                'strip_tags': True,
                'data_postprocessor': extract_title,
                'required': True
            }, {
                'name': 'image',
                'selector_xpath': '//div[@class="b-pinfo"]//img[@class="bp-photo"]/@src',
                'download_single_url': True
            }, {
                'name': 'name_en',
                'data_postprocessor': lambda info, meta: to_pinyin_name(meta['name']),
                'required': True
            }]
        }
    }

myspider = SpiderFactory(ScrapyConfig(), __name__)

