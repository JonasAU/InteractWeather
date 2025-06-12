import cdsapi
import json
import netCDF4 as nc
#import h5netcdf.legacyapi as nc
from datetime import datetime
import netcdftime
import csv
from zipfile import ZipFile
from pathvalidate import sanitize_filename
import requests
import paramiko
import shutil
import pandas as pd

# Stations list
#stations = []
#with open("stations.json") as jsonFile:
#	jsonStations = json.load(jsonFile)
#	for station in jsonStations:
#		stations.append( {"Id": station["StationId"], "Name": station["StationName"], "Latitude": station["Latitude"], "Longitude": station["Longitude"], "HasClimateDate": station["HasClimateData"] } )

# Stations list via openapi
stations = []
response = requests.get("https://interact-gis.org/api/external/stationinformation")
jsonStations = response.json()
for station in jsonStations:
	print(station["Information"]["Latitude"])
	print(station["Information"]["Longitude"])
	stations.append( {"Id": station["StationId"], "Name": station["StationName"], "Latitude": float(station["Information"]["Latitude"]), "Longitude": float(station["Information"]["Longitude"]), "HasClimateData": station["Information"]["HasClimateData"] } )

c = cdsapi.Client()

# loop stations, get data, extract from  netcdf, write to csv file
#csvHeader = ["StationID", "StationName", "Latitude", "Longitude", "Year", "Month", "Air temperature 2m, deg C, monthly average", "Precipition, m, monthly total"]
csvHeader = ["StationID", "Latitude", "Longitude", "Year", "Month", "Air temperature 2m, deg C, monthly average", "Precipition, m, monthly total"]

with open("station_climate.csv", 'w', encoding="UTF8", newline='') as csvFile:
	csvWriter = csv.writer(csvFile)
	csvWriter.writerow(csvHeader)
	for station in stations:
		print(station["Name"])
		print('HasClimateData: ' + str(station['HasClimateData']))

		yearRange = [
		            '{0}'.format(datetime.now().year-1), '{0}'.format(datetime.now().year)
		        ]
		if station['HasClimateData'] != "True" and station['HasClimateData'] != True:
			yearRange = list(range(1950, datetime.now().year+1))

		simplifiedName = ''.join(letter for letter in station["Name"] if letter.isalnum() or letter == ' ')
		filename = sanitize_filename(simplifiedName + "_download.nc.zip")
		# N W S E
		areaBox = [
		            station["Latitude"], station["Longitude"], station["Latitude"]-0.001,
		            station["Longitude"]+0.001
			]

		c.retrieve(
		    'reanalysis-era5-single-levels-monthly-means',
		    {
		        'product_type': 'monthly_averaged_reanalysis',
		        'variable': [
		            '2m_temperature', 'total_precipitation',
		        ],
		        'area': areaBox,
    			'data_format': 'netcdf',
    			'download_format': 'zip',
#			'year': list(range(1950,2024)),
		        'year': yearRange,
		        'month': [
		            '01', '02', '03',
		            '04', '05', '06',
		            '07', '08', '09',
		            '10', '11', '12',
		        ],
		        'time': '00:00',
		    },
		    filename)

		# copy zip
		filenameID = str(station["Id"]) + "_download.nc.zip"
		shutil.copyfile(filename, filenameID)		

		# unzip and process
		stationPath = "./" + str(station["Id"])
		with ZipFile("./" + filenameID) as zipFile:
				zipFile.extractall(stationPath)
		ncFiles = zipFile.namelist()
		print("Extracted files: " + str(ncFiles))
		file_1 = "./" + str(station["Id"]) + "/" + ncFiles[0]
		file_2 = "./" + str(station["Id"]) + "/" + ncFiles[1]
		ds_1 = nc.Dataset(file_1)
		ds_2 = nc.Dataset(file_2)		
		try:
			testvar = ds_1["tp"]
			ds_tp = ds_1
			ds_t2m = ds_2
		except:
			testvar = ds_2["tp"]
			ds_tp = ds_2
			ds_t2m = ds_1


		# show dataset info
		print(ds_t2m)
		print(ds_tp)

		# convert nc times hours since 1900 to datetime
		#--nctime=ds['time'][:]
		#--t_cal=ds['time'].calendar
		#--t_unit = ds.variables['time'].units

		#--converteddates = netcdftime.num2date(nctime,units = t_unit,calendar = t_cal)


		precip = ds_tp['tp'][:]
		temp2m = ds_t2m['t2m'][:]
		#--time = ds['time'][:]		

		# convert nc times to datetime
		nctime = ds_t2m['valid_time'][:]
		t_cal = ds_t2m['valid_time'].calendar
		t_unit = ds_t2m.variables['valid_time'].units
		print("Time unit: " + t_unit)
		print("Time calendar: " + t_cal)
		converteddates = pd.to_datetime(nctime, unit='s') # Datetime
		#netcdftime.num2date(nctime,units = t_unit,calendar = t_cal)		
		print(converteddates)

		# write to csv
		for i in range(0, len(precip)):
			measurementYear = str(converteddates[i].year)
			measurementMonth = str(converteddates[i].month)
			print(measurementYear)
			print(measurementMonth)
			print("Precipitation (m) / month total: " + str(precip[i]))
			print("Air temperature, 2m (Deg C) / month average: " + str(temp2m[i]-273.15))
			#csvWriter.writerow([station["Id"], station["Name"], station["Latitude"], station["Longitude"], measurementYear, measurementMonth, temp2m[i][0][0]-273.15, precip[i][0][0]])
			csvWriter.writerow([station["Id"], station["Latitude"], station["Longitude"], measurementYear, measurementMonth, str(temp2m[i]-273.15).replace('[[', '').replace(']]', ''), str(precip[i]).replace('[[', '').replace(']]', '')])

		#break # temporarily

		
# upload climate data file using sftp
with paramiko.SSHClient() as ssh:
	ssh.load_system_host_keys()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

	ssh.connect('io.erda.au.dk', username='jZxlrPK5er', password='jZxlrPK5er', port=2222, allow_agent=False)

	sftp = ssh.open_sftp()
	sftp.put('station_climate.csv', 'station_climate.csv')
