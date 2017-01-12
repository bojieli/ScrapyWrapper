#coding=utf8
import pymssql
import codecs
import sys

server = "114.215.255.52"
user = "AddDataUser"
password = "Dv*#d~18K"
dbname = "DB_Medicine"

conn = pymssql.connect(server, user, password, dbname, charset="utf8")
cursor = conn.cursor()

table_name = 'FertilityAndReproduction'

table_fields = [
'ID',
'RegionID',
'Region',
'HospitalName',
'TechnologyType',
'OperationalStatus'
]

regions = {}
cursor.execute("SELECT PID, Name FROM TB_Addresses")
num_regions = 0
for row in cursor:
	regions[row[1]] = row[0]
	num_regions += 1
print('load ' + str(num_regions) + ' regions')

def get_region_id(name):
	if name in regions:
		return regions[name]
	if name + u'省' in regions:
		return regions[name + u'省']
	if name + u'市' in regions:
		return regions[name + u'市']
	return None

value_types = ['%s' for x in table_fields]
value_types[0] = 'NEWID()'


cursor.execute("DELETE FROM " + table_name)
cursor.execute("SET ANSI_WARNINGS off")

def insertmany(cursor, table_name, fields, value_types, table_data):
	cursor.execute("INSERT INTO " + table_name + " (" + ",".join(fields) + ") VALUES "
		+ ",".join([ "(" + ",".join(value_types) + ")" for row in table_data ]),
		tuple([item for sublist in table_data for item in sublist]))

def insertshard(cursor, table_name, fields, value_types, table_data):
	shard_size = 1000
	total = len(table_data)
	for i in range(0, total, shard_size):
		shard = table_data[i:i+shard_size]
		insertmany(cursor, table_name, fields, value_types, shard)
		print(i)

table_data = []

with codecs.open(sys.argv[1], 'r', encoding='utf8') as f:
	for line in f:
		fields = line.split('\t')
		fields = [f.strip() for f in fields]
		if len(fields) != 4:
			continue
		if fields[1] == '':
			continue
		record = [
			get_region_id(fields[0]),
			fields[0],
			fields[1],
			fields[2],
			fields[3]
		]
		table_data.append(record)
	print('rows: ' + str(len(table_data)))
	insertshard(cursor, table_name, table_fields, value_types, table_data)
	conn.commit()

conn.close()
