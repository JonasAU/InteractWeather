import netCDF4 as nc
import datetime
import netcdftime

file = "./data.nc"
ds = nc.Dataset(file)

# show dataset info
print(ds)

# convert nc times hours since 1900 to datetime
nctime=ds['time'][:]
t_cal=ds['time'].calendar
t_unit = ds.variables['time'].units

converteddates = netcdftime.num2date(nctime,units = t_unit,calendar = t_cal)


precip = ds['tp'][:]
temp2m = ds['t2m'][:]
time = ds['time'][:]
for i in range(0, len(precip)):
	print(converteddates[i].year)
	print(converteddates[i].month)
	print("Precipitation (m) / month total: " + str(precip[i][0][0][0]))
	print("Air temperature, 2m (Deg C) / month average: " + str(temp2m[i][0][0][0]-273.15))

