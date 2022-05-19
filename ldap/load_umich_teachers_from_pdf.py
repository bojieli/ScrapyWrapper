#/usr/bin/python3
# use pdftotext to convert PDF to text first
import sys
import pymysql

db = pymysql.connect(host='localhost', user='crawler', password='crawler', database='TeacherInfo')
cursor = db.cursor()

def insert_record(info):
    global db, cursor
    table_name = 'umich_teachers_pdf'
    sql = "INSERT INTO " + table_name + " (" + ",".join([ k for k in info ]) + ") VALUES " + "(" + ",".join([ '%s' for v in info ]) + ")"
    data = tuple([ info[key] for key in info ])
    cursor.execute(sql, data)
    db.commit()

def insert_entries(entries):
    load_count = 0
    for entry in entries:
        if len(entry) != 4:
            continue
        info = dict()
        info['name'] = entry[1]
        names = entry[1].split(',')
        if len(names) != 2:
            continue
        info['surname'] = names[0].split(' ')[0]
        info['given_name'] = names[1].split(' ')[0]

        info['title'] = entry[2]
        info['org'] = entry[3]
        insert_record(info)
        load_count += 1
    print('Loaded ' + str(load_count) + ' teachers')

def parse_pdf_results(text):
    records = text.split('\n')
    print(len(records))
    total_headers = 4

    status = 'begin'
    header_count = 0
    body_column = 0
    num_entry_in_page = 0
    entries_in_page = []
    for record in records:
        if status == 'begin':
            if record == 'SALARY RATE OF FACULTY AND STAFF':
                status = 'header'
                header_count = 0
        elif status == 'header':
            if record != '':
                header_count += 1
                if header_count == 1 and record != 'CAMPUS':
                    status = 'header'
                if header_count >= total_headers:
                    status = 'body'
                    body_column = 0
                    num_entry_in_page = 0
                    entries_in_page = []
        elif status == 'body':
            if record == '':
                if len(entries_in_page) > 0:
                    body_column += 1
                    num_entry_in_page = 0
                    if body_column == total_headers:
                        insert_entries(entries_in_page)
                        status = "begin"
            else:
                if body_column == 0:
                    entries_in_page.append([record])
                else:
                    entries_in_page[num_entry_in_page].append(record)
                num_entry_in_page += 1

with open(sys.argv[1], 'r') as f:
    parse_pdf_results(f.read())
