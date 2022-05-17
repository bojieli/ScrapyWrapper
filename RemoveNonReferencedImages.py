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
    to_remove_file = False
    to_remove_db = False
    to_print_noref_file = False
    to_print_noref_db = False
    for argv in sys.argv[4:]:
        if argv == 'remove_file':
            to_remove_file = True
        if argv == 'print_file':
            to_print_noref_file = True
        if argv == 'remove_db':
            to_remove_db = True
        if argv == 'print_db':
            to_print_noref_db = True

    if not re.match(r'[a-zA-Z0-9_-]+', table_name):
        print('Invalid table name')
        return
    if not re.match(r'[a-zA-Z0-9_-]+', column_name):
        print('Invalid table name')
        return
    
    db = pymysql.connect(host='127.0.0.1', user='crawler', password='crawler', database='TeacherInfo')
    cursor = db.cursor()
    cursor.execute('SELECT ' + column_name + ' FROM ' + table_name)

    urls_from_db = dict()
    num_db_records = 0
    for row in cursor:
        if row[0]: # filter out None or empty string
            urls_from_db[row[0]] = True
            num_db_records += 1
    print('Number of records from DB: ' + str(num_db_records))

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
            if to_print_noref_file:
                print('FS file ' + str(num_unused_files) + ' with no db ref: ' + path)
            if to_remove_file:
                os.remove(path)
    if to_remove_file:
        print('Removed number of unused files: ' + str(num_unused_files))
    else:
        print('Number of unused files: ' + str(num_unused_files))

    num_unreferenced_db_records = 0
    for path in urls_from_db:
        if path not in urls_from_fs:
            num_unreferenced_db_records += 1
            if to_print_noref_db:
                print('DB file ' + str(num_unreferenced_db_records) + ' with no FS file: ' + path)
            if to_remove_db:
                cursor.execute('UPDATE ' + table_name + ' SET ' + column_name + ' = NULL WHERE ' + column_name + ' = %s', (path, ))
    if to_remove_db:
        print('Removed number of unreferenced db records: ' + str(num_unreferenced_db_records))
    else:
        print('Number of unreferenced db records: ' + str(num_unreferenced_db_records))

main()
