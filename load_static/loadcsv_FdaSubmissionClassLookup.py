#coding=utf8
import pymssql
import sys

server = "114.215.255.52"
user = "AddDataUser"
password = "Dv*#d~18K"
dbname = "DB_Medicine"

conn = pymssql.connect(server, user, password, dbname, charset="utf8")
cursor = conn.cursor()
table_data = []
f = open(sys.argv[1], 'r')
table_name = sys.argv[2]

fields = ['ID','SubmissionClassCode','SubmissionClassCodeDescription']
value_types = []
table_data = []
first_line = True
for line in f:
	values = line.split(',')
	values = [v.strip().strip('"') for v in values]
	if first_line:
		first_line = False
		value_types.extend(['%s' for v in values])
		print(fields)
		continue
	table_data.append(values)

print(value_types)
print(table_data)

cursor.execute("DELETE FROM " + table_name)
cursor.execute("SET ANSI_WARNINGS off")

def insertmany(cursor, table_name, fields, value_types, table_data):
	sql = "INSERT INTO " + table_name + " (" + ",".join(fields) + ") VALUES " + ",".join([ "(" + ",".join(value_types) + ")" for row in table_data ])
	print(sql)
	cursor.execute(sql,
		tuple([item for sublist in table_data for item in sublist]))

def insertshard(cursor, table_name, fields, value_types, table_data):
	shard_size = 1
	total = len(table_data)
	for i in range(0, total, shard_size):
		shard = table_data[i:i+shard_size]
		insertmany(cursor, table_name, fields, value_types, shard)
		print(i)

insertshard(cursor, table_name, fields, value_types,  table_data)
conn.commit()
conn.close()
