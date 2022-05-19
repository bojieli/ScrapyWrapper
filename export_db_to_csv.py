#!/usr/bin/python3
# -*- coding:utf-8 -*-
import pymysql
import csv
import sys
import re

def main():
    csv_file = sys.argv[1]
    table_name = sys.argv[2]
    if not re.match(r'[a-zA-Z0-9_-]+', table_name):
        print('Invalid table name')
        return
    
    db = pymysql.connect(host='127.0.0.1', user='crawler', password='crawler', database='TeacherInfo', cursorclass=pymysql.cursors.DictCursor)
    cursor = db.cursor()
    cursor.execute('SELECT * FROM ' + table_name)

    f = open(csv_file, 'w')
    writer = csv.writer(f)

    num_records = 0
    is_first = True
    keys = []
    for row in cursor:
        if is_first:
            keys = [ k for k in row if k != 'ID' ]
            is_first = False
            writer.writerow(keys)  # write header
    
        values = [ row[k] for k in keys if k != 'ID' ]
        writer.writerow(values)
        num_records += 1
    
    if num_records == 0:
        print('No results')
    else:
        print('Exported ' + str(num_records) + ' records')
    f.close()

main()
