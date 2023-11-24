import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from sanitize_filename import sanitize
import sys
import traceback

filename = sys.argv[1]
print(filename)
df = pd.read_csv (filename)

years = df.Year.unique()
stations = df.Station.unique()

print(df)

#print(years)
#print(stations)


for station in stations:
	print(station)
	try:
		# filter to station
		dfStation = df.loc[df['Station'] == station]

		my_colors = [(100/255, 100/255, 255/255),(140/255, 140/255, 255/255),(180/255, 180/255, 255/255),(220/255, 220/255, 255/255),(100/255, 100/255, 100/255),(150/255, 150/255, 150/255)]

		# line plot temperature variation from WMO average 1961-1990 period
		plot1 = pd.pivot_table(dfStation.reset_index(),
		               index='Month', columns='Year', values='WMO1DiffTemp'
		              ).plot.bar(title=station, color=my_colors)
		plt.ylabel('Difference to WMO Average (1961-1990) AT 2m, deg C, monthly average')
		plt.savefig('plotWMO1961_1990DiffBar' + sanitize(station) + '_temperature.pdf')

		# line plot temperature variation from WMO average 1991-2020 period
		plot1 = pd.pivot_table(dfStation.reset_index(),
		               index='Month', columns='Year', values='WMO2DiffTemp'
		              ).plot.bar(title=station, color=my_colors)
		plt.ylabel('Difference to WMO Average (1991-2020) AT 2m, deg C, monthly average')
		plt.savefig('plotWMO1991_2020DiffBar' + sanitize(station) + '_temperature.pdf')

		# line plot precipitation variation from WMO average 1961-1990 period
		plot1 = pd.pivot_table(dfStation.reset_index(),
		               index='Month', columns='Year', values='WMO1DiffPrec'
		              ).plot.bar(title=station, color=my_colors)
		plt.ylabel('Difference to WMO Average (1961-1990) Pre, m, monthly total')
		plt.savefig('plotWMO1961_1990DiffBar' + sanitize(station) + '_precipitation.pdf')

		# line plot precipitation variation from WMO average 1991-2020 period
		plot1 = pd.pivot_table(dfStation.reset_index(),
		               index='Month', columns='Year', values='WMO2DiffPrec'
		              ).plot.bar(title=station, color=my_colors)
		plt.ylabel('Difference to WMO Average (1991-2020) Pre, m, monthly total')
		plt.savefig('plotWMO1991_2020DiffBar' + sanitize(station) + '_precipitation.pdf')


	except Exception as e:
		print(f'Error plotting this station, continuing: {str(e)}')
		print(traceback.format_exc())
	finally:
		plt.close()		
