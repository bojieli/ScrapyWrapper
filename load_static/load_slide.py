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

def parse_date(s):
	month_map = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
	x = [v.strip(',') for v in s.split(' ')]
	return x[2] + '-' + format(month_map[x[0]], '02d') + '-' + format(int(x[1]), '02d')

fields = ['ID']
value_types = ['%s']
table_data = []
first_line = True
count = 0
for line in f:
	values = line.split('~')
	values = [v.strip() for v in values]
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
	if len(fields) > 10 and fields[10] =="ApprovalDate":
		try:
			values[9] = parse_date(values[9])
		except:
			values[9] = ''
	if len(fields) > 5 and fields[5] =="ExpireDate":
		try:
			values[4] = parse_date(values[4])
		except:
			values[4] = ''
	if len(fields) > 5 and fields[5] =="ExclusivityDate":
		try:
			values[4] = parse_date(values[4])
		except:
			values[4] = ''

	table_data.append([str(count)] + values)

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
