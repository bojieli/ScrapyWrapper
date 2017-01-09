#coding=utf8
import pymssql
import sys
import dateparser
import codecs
import datetime

server = "114.215.255.52"
user = "AddDataUser"
password = "Dv*#d~18K"
dbname = "DB_Medicine"

conn = pymssql.connect(server, user, password, dbname, charset="utf8")
cursor = conn.cursor()

table_fields = [
'ID',
'PublicationDate',
'RegionID',
'Region',
'HighestTemperature',
'LowestTemperature',
'WindSpeed',
'AirPressure',
'Precipitation',
'Longitude',
'Latitude',
'StationID',
'StationName',
'AverageTemperature',
'DayOfYear'
]

regions = {}
cursor.execute("SELECT PID, Name FROM TB_Addresses")
num_regions = 0
for row in cursor:
	regions[row[1]] = row[0]
	num_regions += 1
print('load ' + str(num_regions) + ' regions')

def get_region_id(name1, name2):
	if name1 in regions:
		return regions[name1]
	if name2 in regions:
		return regions[name2]
	if name2 + u'省' in regions:
		return regions[name2 + u'省']
	return None

value_types = ['%s' for x in table_fields]
value_types[0] = 'NEWID()'

table_data = []

stations = {}
with codecs.open('WeatherStations.txt', 'r', encoding='utf8') as f:
	for line in f:
		fields = line.split('\t')
		fields = [f.strip() for f in fields]
		stations[fields[0]] = fields


table_name = 'HistoricalWeather'
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

from os import listdir
from os.path import isfile, join
basedir = 'climate-data'
onlyfiles = [f for f in listdir(basedir) if isfile(join(basedir, f))]


for filename in onlyfiles:
	if filename.endswith('.txt'):
		with open(join(basedir, filename), 'r') as f:
			table_data = []
			firstline = True
			for line in f:
				if firstline:
					firstline = False
					continue
				fields = line.split(' ')
				fields = [f.strip() for f in fields]
				try:
					station = stations[fields[0]]
					record = [
						(datetime.date(2016, 1, 1) + datetime.timedelta(days=int(fields[2])-1)).strftime('%Y-%m-%d'),
						get_region_id(station[2], station[1]),
						station[1], #region
						fields[4], #high
						fields[5], #low
						fields[9], #wind
						fields[6], #pressure
						fields[7], #precipi
						station[3], #long
						station[4], #lat
						station[0], #id
						station[2], #name
						fields[3], # avg
						fields[2]  # day
					]
				except:
					continue
				table_data.append(record)
			print('rows: ' + str(len(table_data)))
			insertshard(cursor, table_name, table_fields, value_types, table_data)
			conn.commit()

conn.close()
