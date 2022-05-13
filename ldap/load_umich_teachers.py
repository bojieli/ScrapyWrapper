#/usr/bin/python3
import os
import pymysql

db = pymysql.connect(host='localhost', user='crawler', password='crawler', database='TeacherInfo')
cursor = db.cursor()

def insert_record(info):
    global db, cursor
    table_name = 'umich_teachers'
    sql = "INSERT INTO " + table_name + " (" + ",".join([ k for k in info ]) + ") VALUES " + "(" + ",".join([ '%s' for v in info ]) + ")"
    data = tuple([ info[key] for key in info ])
    cursor.execute(sql, data)
    db.commit()
    print(info)

def to_ldap_cmd(prefix):
    return 'ldapsearch -x -H ldap://ldap.umich.edu -b "ou=People,dc=umich,dc=edu" "(&(ou=*Faculty*)(uid=' + prefix + '*))"'

def parse_ldap_results(text):
    records = text.split('\n\n')
    teacher_count = 0
    for record in records:
        info = dict()
        lines = record.split('\n')
        num_lines = len(lines)
        for index in range(num_lines):
            line = lines[index]
            if line.startswith('#'):
                continue
            if line.startswith(' '):
                continue
            kv = line.split(':')
            if len(kv) != 2:
                continue
            key = kv[0].strip()
            value = kv[1].strip()
            for next_index in range(index + 1, num_lines):
                next_line = lines[next_index]
                if next_line.startswith(' '):
                    value += next_line.strip()
                else:
                    break

            if key == 'displayName':
                info['name'] = value
            elif key == 'mail':
                info['email'] = value
            elif key == 'umichTitle':
                info['title'] = value
            elif key == 'ou':
                if value.find('Faculty') != -1:
                    org = value.split('-')[0].strip()
                    if 'org' in info:
                        info['org'] += '; ' + org
                    else:
                        info['org'] = org
            elif key == 'givenName':
                info['given_name'] = value
            elif key == 'sn':
                info['surname'] = value
        if 'email' not in info or 'name' not in info:
            continue
        info['original_info'] = record
        insert_record(info)
        teacher_count += 1
    print('Loaded ' + str(teacher_count) + ' teachers')

def append_prefix_and_retry(prefix):
    for c in range(0, 26):
        curr_prefix = prefix + chr(ord('a') + c)
        cmd = to_ldap_cmd(curr_prefix)
        results = os.popen(cmd).read()
        if results.find('Size limit exceeded') != -1:
            append_prefix_and_retry(curr_prefix)
        elif results.find('result: 0 Success') != -1:
            parse_ldap_results(results)
        else:
            print('Invalid search result for ldap cmd: ' + cmd)

for c in range(0, 26):
    prefix = chr(ord('a') + c)
    append_prefix_and_retry(prefix)
