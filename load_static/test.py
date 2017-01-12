#coding=utf8
import pymssql

server = "114.215.255.52"
user = "AddDataUser"
password = "Dv*#d~18K"
dbname = "DB_Medicine"

conn = pymssql.connect(server, user, password, dbname, charset="utf8")
cursor = conn.cursor()
#cursor.executemany(
#    "INSERT INTO persons VALUES (%d, %s, %s)",
#    [(1, 'John Smith', 'John Doe'),
#     (2, 'Jane Doe', 'Joe Dog'),
#     (3, 'Mike T.', 'Sarah H.')])
## you must call commit() to persist your data if you don't set autocommit to True
#conn.commit()

table_data = []
f = open('data', 'r')
for line in f:
	fields = line.split('\t')
	if len(fields) != 3:
		continue
	for i in range(0,3):
		fields[i] = fields[i].strip().decode('utf8')
	table_data.append(fields)


cursor.execute("DELETE FROM NationalAffordableDrugList")

def insertmany(cursor, table_name, fields, value_types, table_data):
	cursor.execute("INSERT INTO " + table_name + " (" + ",".join(fields) + ") VALUES "
		+ ",".join([ "(" + ",".join(value_types) + ")" for row in table_data ]),
		tuple([item for sublist in table_data for item in sublist]))

insertmany(cursor,
	"NationalAffordableDrugList",
	["ID", "SerialNumber", "DrugName", "DosageName"],
	["NEWID()", "%s", "%s", "%s"],
	table_data)
	
conn.commit()

cursor.execute('SELECT * FROM NationalAffordableDrugList')
row = cursor.fetchone()
while row:
    print("ID=%d, Name=%s" % (row[0], row[1]))
    row = cursor.fetchone()

conn.close()
