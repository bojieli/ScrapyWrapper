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


srctable_name = 'DrugClassification'
classification_map = {}

cursor.execute('SELECT ID, ClassificationNumber FROM ' + srctable_name)
row = cursor.fetchone()
count = 0
while row:
    classification_map[row[1]] = row[0]
    row = cursor.fetchone()
    count += 1

print('Load classification ' + str(count))

table_data = []
f = open('national_traditional.txt', 'r')
count = 0
for line in f:
    column_count = 6
    fields = line.split('\t')
    if len(fields) != column_count:
        continue
    for i in range(0,column_count):
        fields[i] = fields[i].strip().strip('"').decode('utf8')
    if fields[0] == "":
        continue
    if fields[4] not in classification_map:
        print('Error: ' + fields[4])
        continue
    fields[4] = classification_map[fields[4]]
    table_data.append(['1', fields[1], '', fields[5], '', fields[3], fields[4], fields[0]])
    count += 1

print('Load traditional ' + str(count))

f = open('national_non_traditional.txt', 'r')
count = 0
for line in f:
    column_count = 7
    fields = line.split('\t')
    if len(fields) != column_count:
        continue
    for i in range(0,column_count):
        fields[i] = fields[i].strip().strip('"').decode('utf8')
    if fields[0] == "":
        continue
    if fields[5] not in classification_map:
        print('Error: ' + fields[5])
        continue
    fields[5] = classification_map[fields[5]]
    table_data.append(['0'] + fields)
    count += 1

print('Load non-traditional ' + str(count))


table_name= 'NationalDrugReimbursementList'

cursor.execute("DELETE FROM " + table_name)

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

insertshard(cursor,
    table_name,
    ["ID", "IsTraditionalMedicine", "DrugName", "DrugNameEnglish", "DosageType", "Paym", "Classification", "DrugClassificationID", "SerialNumber"],
    ["NEWID()", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s"],
    table_data)
    
conn.commit()

#cursor.execute('SELECT * FROM ' + table_name)
#row = cursor.fetchone()
#while row:
#    row = cursor.fetchone()

conn.close()
