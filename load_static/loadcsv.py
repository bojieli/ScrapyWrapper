#coding=utf8
import pymssql
import sys
import csv

server = "114.215.255.52"
user = "AddDataUser"
password = "Dv*#d~18K"
dbname = "DB_Medicine"

conn = pymssql.connect(server, user, password, dbname, charset="utf8")
cursor = conn.cursor()
table_data = []
f = open(sys.argv[1], 'r')
table_name = sys.argv[2]

fields = ['ID']
value_types = ['NEWID()']
table_data = []
first_line = True
count = 0
for values in csv.reader(f):
	if first_line:
		first_line = False
		if "ID" in values:
			fields = values
			value_types = ['%s' for v in values]
		else:
			fields.extend(values)
			value_types.extend(['%s' for v in values])
		print(fields)
		continue
	count += 1
	table_data.append(values)

cursor.execute("DELETE FROM " + table_name)
cursor.execute("SET ANSI_WARNINGS off")

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
		conn.commit()
		print(i)

insertshard(conn, cursor, table_name, fields, value_types,  table_data)
conn.close()
