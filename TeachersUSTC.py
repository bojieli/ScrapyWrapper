#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
from scrapywrapper.helper import to_pinyin_name
from urllib.request import urlopen
import lxml.html
import csv
import re

teacher_emails = dict()
with open('teachers.csv', 'r') as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        name = row[1]
        email = row[3]
        if name in teacher_emails:
            print('Duplicate teacher name: ' + name + ' ' + email)
        teacher_emails[name] = email

def find_email_from_content(text):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    result = re.findall(regex, text)
    for email in result:
        if email.strip() == 'gradschl@ustc.edu.cn':
            continue
        else:
            return email.strip()
    return None

def find_email(name, meta):
    text = meta['$$body']
    email = find_email_from_content(text)
    if email:
        print('Teacher ' + name + ': Found email ' + email + ' from content')
        return email

    # email not found in body
    homepage = extract_homepage(text, '个人主页：', check_http=True)
    if homepage:
        try:
            content = urlopen(homepage, timeout=10).read().decode('utf-8')
            text = lxml.html.document_fromstring(content).text_content()
            email = find_email_from_content(text)
            if email:
                print('Teacher ' + name + ': Found email ' + email + ' from homepage: ' + homepage)
                return email
            else:
                print('Teacher ' + name + ': EMAIL NOT FOUND from homepage: ' + homepage)
        except Exception as e:
            print(e)

    # homepage not found
    if name in teacher_emails:
        print('Teacher ' + name + ': Found email ' + teacher_emails[name] + ' from icourse DB')
        return teacher_emails[name]
    else:
        print('Teacher ' + name + ' EMAIL NOT FOUND')
        return None

def extract_homepage(haystack, needle, check_http=False):
    haystack = lxml.html.document_fromstring(haystack).text_content()
    index = haystack.find(needle)
    if index == -1:
        print('Homepage not found!')
        return None
    else:
        substr = haystack[index + len(needle):].strip()
        result = re.search(r'[\s]*[^\s]+', substr)
        if result:
            result = result.group(0).strip()
            print('Homepage: ' + result)
            if check_http:
                return result if result.startswith('http') else None
            else:
                return None if '：' in result else result
        else:
            return None

class ScrapyConfig(ScrapyWrapperConfig):
    #use_http_proxy = False
    file_basedir = 'teacher_images/USTC'
    begin_urls = ["https://dsxt.ustc.edu.cn/admin_sgdsmd_xnw.asp"]
    steps = {
        "begin": {
            'res': {
                'selector_xpath': '//a/@href',
                'selector_regex': '(.*zj_js.asp.*zzid=.*)',
                'next_step': 'profile'
            },
        },
        'profile': {
            'res': {
                'next_step': 'db'
            }
        },
        "db": {
            'type': "db",
            'table_name': "ustc_teachers",
            #'unique': ['email'],
            'upsert': True,
            'fields': [{
                'name': "email",
                'selector_xpath': '//td[@class="ustc03"]',
                'data_postprocessor': lambda name,meta: find_email(name, meta),
                'required': True
            }, {
                'name': 'name',
                'selector_xpath': '//td[@class="ustc03"]',
                'required': True
            }, {
                'name': 'name_en',
                'selector_xpath': '//td[@class="ustc03"]',
                'data_postprocessor': lambda name,_: to_pinyin_name(name),
                'required': True
            }, {
                'name': 'org',
                'selector_xpath': '//td[@class="ustc04"]',
                'data_postprocessor': lambda info,_: extract_homepage(info, '单位：')
            }, {
                'name': "url",
                'selector_xpath': '//td[@class="ustc04"]',
                'data_postprocessor': lambda info,_: extract_homepage(info, '个人主页：', check_http=True)
            }, {
                'name': 'image',
                'selector_regex': '(fj_show.asp\?fjid=\d+)',
                'download_single_url': True
            }]
        }
    }

myspider = SpiderFactory(ScrapyConfig(), __name__)

