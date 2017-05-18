#coding=utf8
import pymssql
import sys
import dateparser

server = "114.215.255.52"
user = "AddDataUser"
password = "Dv*#d~18K"
dbname = "DB_Medicine"

conn = pymssql.connect(server, user, password, dbname, charset="utf8")
cursor = conn.cursor()
table_data = []
f = open(sys.argv[1], 'r')
table_name = sys.argv[2]
national = sys.argv[3]

def parse_date(s):
    month_map = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
    x = [v.strip(',') for v in s.split(' ')]
    return x[2] + '-' + format(month_map[x[0]], '02d') + '-' + format(int(x[1]), '02d')

cursor.execute("DELETE FROM " + table_name + ' WHERE IsTraditionalMedicine = %s', (national))
cursor.execute("SET ANSI_WARNINGS off")

fields = ['ID','IsTraditionalMedicine','ClassificationNumber','ClassificationName']
value_types = ['NEWID()','%s','%s','%s']
table_data = []
count = 0
for line in f:
    values = [ f.strip() for f in line.split('\t') ]
    if len(values) != 2:
        continue
    if values[0] == '' or values[1] == '':
        continue
    count += 1
    table_data.append([national] + values)

print('Inserting ' + str(count) + ' records')

def insertmany(cursor, table_name, fields, value_types, table_data):
    cursor.execute("INSERT INTO " + table_name + " (" + ",".join(fields) + ") VALUES "
        + ",".join([ "(" + ",".join(value_types) + ")" for row in table_data ]),
        tuple([item for sublist in table_data for item in sublist]))

def insertshard(conn, cursor, table_name, fields, value_types, table_data):
    shard_size = 1000
    total = len(table_data)
    for i in range(0, total, shard_size):
        shard = table_data[i:i+shard_size]
        insertmany(cursor, table_name, fields, value_types, shard)
        print(i)

insertshard(conn, cursor, table_name, fields, value_types,  table_data)
conn.commit()
conn.close()
