import cdsapi
import json
import netCDF4 as nc
from datetime import datetime
import netcdftime
import csv
from zipfile import ZipFile
from sanitize_filename import sanitize
import requests
import paramiko

# Stations list
#stations = []
#with open("stations.json") as jsonFile:
#	jsonStations = json.load(jsonFile)
#	for station in jsonStations:
#		stations.append( {"Id": station["StationId"], "Name": station["StationName"], "Latitude": station["Latitude"], "Longitude": station["Longitude"], "HasClimateDate": station["HasClimateData"] } )

# Stations list via openapi
stations = []
response = requests.get("https://interact-gis.stage.its.umu.se/api/StationList")
jsonStations = response.json()
for station in jsonStations:
	stations.append( {"Id": station["StationId"], "Name": station["StationName"], "Latitude": station["Latitude"], "Longitude": station["Longitude"], "HasClimateData": station["HasClimateData"] } )

c = cdsapi.Client()

# loop stations, get data, extract from  netcdf, write to csv file
#csvHeader = ["StationID", "StationName", "Latitude", "Longitude", "Year", "Month", "Air temperature 2m, deg C, monthly average", "Precipition, m, monthly total"]
csvHeader = ["StationID", "Latitude", "Longitude", "Year", "Month", "Air temperature 2m, deg C, monthly average", "Precipition, m, monthly total"]

with open("station_climate.csv", 'w', encoding="UTF8") as csvFile:
	csvWriter = csv.writer(csvFile)
	csvWriter.writerow(csvHeader)
	for station in stations:
		print(station["Name"])
		print('HasClimateData: ' + str(station['HasClimateData']))

		yearRange = [
		            '{0}'.format(datetime.now().year-1), '{0}'.format(datetime.now().year)
		        ]
		if station['HasClimateData'] != True:
			yearRange = list(range(1950,2024))

		filename = sanitize(station["Name"] + "_download.nc")
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
		        'format': 'netcdf',
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

		# process netcdf

		ds = nc.Dataset(filename)

		# show dataset info
		print(ds)

		# convert nc times hours since 1900 to datetime
		#--nctime=ds['time'][:]
		#--t_cal=ds['time'].calendar
		#--t_unit = ds.variables['time'].units

		#--converteddates = netcdftime.num2date(nctime,units = t_unit,calendar = t_cal)


		precip = ds['tp'][:]
		temp2m = ds['t2m'][:]
		#--time = ds['time'][:]
		date=ds['date'][:]

		# write to csv
		for i in range(0, len(precip)):
			measurementYear = datetime.strptime(str(date[i]), '%Y%m%d').year
			measurementMonth = datetime.strptime(str(date[i]), '%Y%m%d').month
			print(measurementYear)
			print(measurementMonth)
			print("Precipitation (m) / month total: " + str(precip[i][0][0]))
			print("Air temperature, 2m (Deg C) / month average: " + str(temp2m[i][0][0]-273.15))
			#csvWriter.writerow([station["Id"], station["Name"], station["Latitude"], station["Longitude"], measurementYear, measurementMonth, temp2m[i][0][0]-273.15, precip[i][0][0]])
			csvWriter.writerow([station["Id"], station["Latitude"], station["Longitude"], measurementYear, measurementMonth, temp2m[i][0][0]-273.15, precip[i][0][0]])

		break # temporarily

		
# upload climate data file using sftp
with paramiko.SSHClient() as ssh:
	ssh.load_system_host_keys()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

	ssh.connect('io.erda.au.dk', username='jZxlrPK5er', password='jZxlrPK5er', port=2222, allow_agent=False)

	sftp = ssh.open_sftp()
	sftp.put('station_climate.csv', 'station_climate_testupload.csv')
