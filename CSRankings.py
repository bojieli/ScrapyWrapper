#/usr/bin/python3
# -*- coding:utf-8 -*-
from scrapywrapper.wrapper import SpiderFactory
from scrapywrapper.config import ScrapyWrapperConfig
import re
import json
from io import StringIO
import csv
import cv2

def parse_csv(text, meta):
    f = StringIO(text.decode('utf-8'))
    reader = csv.reader(f)
    header = None
    records = []
    for row in reader:
        if not header:
            header = row
            continue
        row_dict = dict()
        for index in range(len(header)):
            row_dict[header[index]] = row[index]
        records.append(json.dumps(row_dict))
    print(header)
    print('Number of records: ' + str(len(records)))
    return records

def is_human_face(image_path, cascasdepath="haarcascade_frontalface_default.xml"):
    image = cv2.imread(image_path)
    if image is None:
        return False
    (h, w) = image.shape[:2]
    if h >= w * 2 or w >= h * 2:  # aspect ratio does not look like a face
        return False

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cascasdepath)
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor = 1.2,
        minNeighbors = 5,
        minSize = (30,30)
        )
    return len(faces) == 1

def find_human_faces(html, meta):
    if '$$image_urls' not in meta:
        return None
    # $$image_urls: [ (filepath, url) ]
    files = set([ info[0] for info in meta['$$image_urls'] ])
    print(files)
    valid_files = set()
    for filepath in files:
        if is_human_face(filepath):
            valid_files.add(filepath)
    if len(valid_files) == 0:
        return None
    return " ".join(valid_files)

def parse_email(text, meta):
    emails = set()
    results = re.finditer(r'[A-Za-z0-9-_.]+\s*[\(\[\{]*(at|AT|@)[\)\]\}]*\s*[A-Za-z0-9-_]+\s*([\(\[\{]*(dot|DOT|\.)[\)\]\}]*\s*[A-Za-z0-9-_]+)+', text)
    for result in results:
        email = result.group(0)
        email = email.replace('at', '@').replace('AT', '@').replace('dot', '.').replace('DOT', '.')
        email = re.sub(r'[\s\(\[\{\)\]\}]', '', email)
        emails.add(email)
    if len(emails) == 0:
        return None
    return " ".join(emails)

def find_edu_email(text, meta):
    if 'possible_emails' not in meta:
        return None
    if meta['possible_emails'] is None:
        return None
    emails = meta['possible_emails'].split()
    for email in emails:
        if email.endswith('.edu'):
            return email
    for email in emails:
        if email.find('.edu.') != -1:
            return email
    return None

class ScrapyConfig(ScrapyWrapperConfig):
    file_basedir = 'teacher_images/csrankings'
    begin_urls = ["http://csrankings.org/csrankings.csv"]
    steps = {
        "begin": {
            'res': {
                'selector': parse_csv,
                'next_step': 'parse_row',
                'required': True
            }
        },
        'parse_row': {
            'type': 'intermediate',
            'fields': [{
                'name': 'name',
                'selector_json': 'name',
                'data_postprocessor': lambda name,_: re.sub(r' [0-9]+$', '', name),
                'required': True
            }, {
                'name': 'dblp_name',
                'selector_json': 'name',
                'required': True
            }, {
                'name': 'university',
                'selector_json': 'affiliation',
                'required': True
            }, {
                'name': 'url',
                'selector_json': 'homepage',
                'required': True
            }, {
                'name': 'scholarid',
                'selector_json': 'scholarid',
                'data_validator': lambda name,_: name != 'NOSCHOLARPAGE',
            }],
            'res': {
                'name': 'url',
                'selector_json': 'homepage',
                'next_step': 'homepage',
            }
        },
        'homepage': {
            'res': {
                'next_step': 'db'
            }
        },
        "db": {
            'type': "db",
            'table_name': "csrankings",
            'unique': ['dblp_name', 'university'],
            'upsert': True,
            'print_record': True,
            'fields': [{
                'name': 'image',
                'download_images': True,
                'post_download_processor': find_human_faces,
            }, {
                'name': 'possible_emails',
                'strip_tags': True,
                'data_postprocessor': parse_email,
            }, {
                'name': 'email',
                'data_postprocessor': find_edu_email,
                'dependencies': ['possible_emails'],
            }]
        }
    }

myspider = SpiderFactory(ScrapyConfig(), __name__)

#import sys
#if len(sys.argv) == 2:
#    print(is_human_face(sys.argv[1]))
