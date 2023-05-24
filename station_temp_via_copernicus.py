import cdsapi

# Stations list
stations = [
		{"id": 1, "name": "Abisko", "lat": 56, "lon": 12, "climate": 0 },
		{"id": 2, "name": "Nuuk", "lat": 57, "lon": 13, "climate": 0 }
	]

c = cdsapi.Client()

for station in stations:

	c.retrieve(
	    'reanalysis-era5-land-monthly-means',
	    {
	        'product_type': 'monthly_averaged_reanalysis',
	        'variable': [
	            '2m_temperature', 'skin_temperature', 'total_precipitation',
	        ],
	        'area': [
	            station["lat"], station["lon"], station["lat"]-0.001,
	            station["lon"]+0.001
	        ],
	        'format': 'netcdf.zip',
	        'year': [
	            '2019', '2020', '2021',
	            '2022', '2023',
	        ],
	        'month': [
	            '01', '02', '03',
	            '04', '05', '06',
	            '07', '08', '09',
	            '10', '11', '12',
	        ],
	        'time': '00:00',
	    },
	    station["name"] + 'download.netcdf.zip')
