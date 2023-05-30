import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sanitize_filename import sanitize

df = pd.read_csv ('stationClimateERA5.csv')

years = df.Year.unique()
stations = df.StationName.unique()

#print(years)
#print(stations)

for station in stations:
	print(station)
	try:
		dfFilter = df.loc[df['StationName'] == station]

		dfFilter = dfFilter.loc[dfFilter['Air temperature 2m, deg C, monthly average'] != '--']
		plot1 = pd.pivot_table(dfFilter.reset_index(),
		               index='Month', columns='Year', values='Air temperature 2m, deg C, monthly average'
		              ).plot.bar(title=station)
		plt.ylabel('Air temperature 2m, deg C, monthly average')
		plt.savefig('plot' + sanitize(station) + '_temperature.pdf')


		dfFilter = dfFilter.loc[dfFilter['Precipition, m, monthly total'] != '--']
		plot1 = pd.pivot_table(dfFilter.reset_index(),
		               index='Month', columns='Year', values='Precipition, m, monthly total'
		              ).plot.bar(title=station)
		plt.ylabel('Total precipition / day, m, monthly average')
		plt.savefig('plot' + sanitize(station) + '_precipitation.pdf')

	except:
		print('Error plotting this station, continuing')
	finally:
		plt.close()		
