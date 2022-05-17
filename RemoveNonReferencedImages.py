#!/usr/bin/python3
# -*- coding:utf-8 -*-
import pymysql
import sys
import re
import os

def main():
    folder_path = sys.argv[1]
    table_name = sys.argv[2]
    column_name = sys.argv[3]
    if not re.match(r'[a-zA-Z0-9_-]+', table_name):
        print('Invalid table name')
        return
    
    db = pymysql.connect(host='127.0.0.1', user='crawler', password='crawler', database='TeacherInfo')
    cursor = db.cursor()
    num_records = cursor.execute('SELECT ' + column_name + ' FROM ' + table_name)

    urls_from_db = dict()
    for row in cursor:
        urls_from_db[row[0]] = True
    print('Number of records from DB: ' + str(num_records))

    urls_from_fs = dict()
    num_urls_from_fs = 0
    for f in os.listdir(folder_path):
        filepath = os.path.join(folder_path, f)
        if os.path.isfile(filepath):
            urls_from_fs[filepath] = True
            num_urls_from_fs += 1
    print('Number of records from FS: ' + str(num_urls_from_fs))

    num_unused_files = 0
    for path in urls_from_fs:
        if path not in urls_from_db:
            num_unused_files += 1
    print('Number of unused files: ' + str(num_unused_files))

    num_unreferenced_db_records = 0
    for path in urls_from_db:
        if path not in urls_from_fs:
            num_unreferenced_db_records += 1
    print('Number of unreferenced db records: ' + str(num_unreferenced_db_records))

main()
