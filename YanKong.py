#/usr/bin/python
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
import json
import hashlib

def get_professor(text, meta):
    obj = json.loads(text)
    professors = []
    for univ in obj:
        for org in obj[univ]:
            for professor_name in obj[univ][org]:
                professors.append(univ + '////' + org + '////' + professor_name)
    return professors

def build_professor_url(text, meta):
    label = text.replace('////', '')
    sha1 = hashlib.sha1(label.encode('utf-8')).hexdigest()
    return 'https://rms-api.realmofresearch.com/reviews/' + sha1

class ScrapyConfig(ScrapyWrapperConfig):
    begin_urls = ["https://rms-api.realmofresearch.com/index/CPdf3hw5jV6y5Xk6lQzt81G46vVA0dRl"]
    steps = {
        "begin": {
            'res': {
                'selector': get_professor,
                'next_step': 'build_professor_url'
            },
        },
        'build_professor_url': {
            'type': 'intermediate',
            'fields': [{
                'name': 'university',
                'selector': lambda x,_: x.split('////')[0],
                'required': True
            }, {
                'name': 'org',
                'selector': lambda x,_: x.split('////')[1],
                'required': True
            }, {
                'name': 'professor',
                'selector': lambda x,_: x.split('////')[2],
                'required': True
            }],
            'res': {
                'selector': build_professor_url,
                'next_step': 'professor'
            }
        },
        'professor': {
            'res': {
                'next_step': 'db'
            }
        },
        "db": {
            'type': "db",
            'table_name': "yankong_reviews",
            'fields': [{
                'name': 'publish_time',
                'selector_json': 'created_at',
                'required': True
            }, {
                'name': 'content',
                'selector_json': 'description',
                'required': True
            }, {
                'name': 'rate',
                'selector_json': 'rate',
            }, {
                'name': 'upvote_count',
                'selector_json': 'count',
            }, {
                'name': 'studentProfRelation',
                'selector_json': 'studentProfRelation',
            }, {
                'name': 'studentSalary',
                'selector_json': 'studentSalary',
            }, {
                'name': 'jobPotential',
                'selector_json': 'jobPotential',
            }, {
                'name': 'workingTime',
                'selector_json': 'workingTime',
            }, {
                'name': 'researchFunding',
                'selector_json': 'researchFunding',
            }, {
                'name': 'academic',
                'selector_json': 'academic',
            }, {
                'name': 'displayed_author',
                'selector_json': 'displayed_author',
            }]
        }
    }

myspider = SpiderFactory(ScrapyConfig(), __name__)

