#coding=utf8
import pymssql

server = "114.215.255.52"
user = "AddDataUser"
password = "Dv*#d~18K"
dbname = "DB_Medicine"

conn = pymssql.connect(server, user, password, dbname, charset="utf8", autocommit=True)
conn2= pymssql.connect(server, user, password, dbname, charset="utf8", autocommit=True)
cursor = conn.cursor()
cursor2 = conn2.cursor()
#cursor.executemany(
#    "INSERT INTO persons VALUES (%d, %s, %s)",
#    [(1, 'John Smith', 'John Doe'),
#     (2, 'Jane Doe', 'Joe Dog'),
#     (3, 'Mike T.', 'Sarah H.')])
## you must call commit() to persist your data if you don't set autocommit to True
#conn.commit()


srctable_name = 'DrugRetailPriceCap'
classification_map = {}

cursor.execute('SELECT ID, DrugManufacturerName FROM DrugRetailPriceCap WHERE RetailPriceCap = 0 AND isnumeric(DrugManufacturerName) = 1')
for row in cursor:
    print("ID=%s, Price=%s" % (row[0], row[1]))
    cursor2.execute('UPDATE DrugRetailPriceCap SET RetailPriceCap = %s, DrugManufacturerName = NULL WHERE ID = %s', (row[1], row[0]))

