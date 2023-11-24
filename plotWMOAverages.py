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
stations = df.StationName.unique()

print(df)

#print(years)
#print(stations)

for station in stations:
	print(station)
	try:
		# wmo averages 1961 - 1990
		dfFilterWMO1 = df.loc[df['StationName'] == station]
		dfFilterWMO1 = dfFilterWMO1.loc[(dfFilterWMO1['Year'] >= 1961) & (dfFilterWMO1['Year'] <= 1990)]
		dfFilterWMO1['Period'] = '1961-1990'

		# wmo averages 1991 - 2020
		dfFilterWMO2 = df.loc[df['StationName'] == station]
		dfFilterWMO2 = dfFilterWMO2.loc[(dfFilterWMO2['Year'] >= 1991) & (dfFilterWMO2['Year'] <= 2020)]
		dfFilterWMO2['Period'] = '1991-2020'

		# recent years
		dfFilterRecent = df.loc[df['StationName'] == station]
		dfFilterRecent = dfFilterRecent.loc[(dfFilterRecent['Year'] >= 2020)]
		dfFilterRecent['Period'] = df['Year']

		# plot temperature / months
		dfFilterWMO1 = dfFilterWMO1.loc[dfFilterWMO1['Air temperature 2m, deg C, monthly average'] != '--']
		dfFilterWMO2 = dfFilterWMO2.loc[dfFilterWMO2['Air temperature 2m, deg C, monthly average'] != '--']
		dfFilterRecent = dfFilterRecent.loc[dfFilterRecent['Air temperature 2m, deg C, monthly average'] != '--']

		dfAll = pd.concat([dfFilterWMO1, dfFilterWMO2, dfFilterRecent])

		dfAll['Air temperature 2m, deg C, monthly average'] = pd.to_numeric(dfAll["Air temperature 2m, deg C, monthly average"], downcast="float")
		dfAll['Precipition, m, monthly total'] = pd.to_numeric(dfAll['Precipition, m, monthly total'], downcast="float")
		dfAll['averagePeriodTemperature'] = dfAll.groupby(['StationName', 'Period', 'Month'])['Air temperature 2m, deg C, monthly average'].transform(np.mean)
		dfAll['averagePeriodPrecipitation'] = dfAll.groupby(['StationName', 'Period', 'Month'])['Precipition, m, monthly total'].transform(np.mean)
		print(dfAll)
		
		my_colors = [(100/255, 100/255, 255/255),(140/255, 140/255, 255/255),(180/255, 180/255, 255/255),(220/255, 220/255, 255/255),(100/255, 100/255, 100/255),(150/255, 150/255, 150/255)]

		plot1 = pd.pivot_table(dfAll.reset_index(),
		               index='Month', columns='Period', values='Air temperature 2m, deg C, monthly average'
		              ).plot.line(title=station, color=mycolors)
		plt.ylabel('Air temperature 2m, deg C, monthly average')
		plt.savefig('plotWMO' + sanitize(station) + '_temperature.pdf')

		plot2 = pd.pivot_table(dfAll.reset_index(),
		               index='Month', columns='Period', values='Precipition, m, monthly total'
		              ).plot.line(title=station, color=mycolors)
		plt.ylabel('Precipition, m, monthly total')
		plt.savefig('plotWMO' + sanitize(station) + '_precipitation.pdf')

		# recent years precipitation
#		dfFilter = dfFilter.loc[dfFilter['Precipition, m, monthly total'] != '--']

		# timeseries plot all years line
		#dfFilter = df.loc[df['StationName'] == station]
		#dfFilter = dfFilter.loc[dfFilter['Air temperature 2m, deg C, monthly average'] != '--']
		#dfFilter = dfFilter.loc[dfFilter['Precipition, m, monthly total'] != '--']
		#print(dfFilter)
		#dfSeasonal = dfFilter.copy()
		#dfSeasonal['Air temperature 2m, deg C, monthly average'] = pd.to_numeric(dfSeasonal["Air temperature 2m, deg C, monthly average"], downcast="float")
		#dfSeasonal['Precipition, m, monthly total'] = pd.to_numeric(dfSeasonal['Precipition, m, monthly total'], downcast="float")
		#dfSeasonal['averageTemperature'] = dfSeasonal.groupby(['StationName', 'Year', 'Season'])['Air temperature 2m, deg C, monthly average'].transform(np.mean)
		#dfSeasonal['averagePrecipitation'] = dfSeasonal.groupby(['StationName', 'Year', 'Season'])['Precipition, m, monthly total'].transform(np.mean)
		#print(dfSeasonal)
		#dfSeasonal = dfSeasonal.drop_duplicates(subset=['StationName', 'Year', 'Season', 'averageTemperature', 'averagePrecipitation'])
		#print(dfSeasonal)

		#pd.pivot_table(dfSeasonal.reset_index(),
		#       index='Year', columns="Season", values='averagePrecipitation'
		#      ).plot.line(title=station)
		#plt.ylabel('Precipitation')

		#locator = matplotlib.ticker.MultipleLocator(10)
		#plt.gca().xaxis.set_major_locator(locator)
		#formatter = matplotlib.ticker.StrMethodFormatter("{x:.0f}")
		#plt.gca().xaxis.set_major_formatter(formatter)

		#plt.savefig('plotLine' + sanitize(station) + '_precipitation.pdf')

		#pd.pivot_table(dfSeasonal.reset_index(),
		#       index='Year', columns="Season", values='averageTemperature'
		#      ).plot.line(title=station)
		#plt.ylabel('Temperature')

		#locator = matplotlib.ticker.MultipleLocator(10)
		#plt.gca().xaxis.set_major_locator(locator)
		#formatter = matplotlib.ticker.StrMethodFormatter("{x:.0f}")
		#plt.gca().xaxis.set_major_formatter(formatter)

		#plt.savefig('plotLine' + sanitize(station) + '_temperature.pdf')

	except Exception as e:
		print(f'Error plotting this station, continuing: {str(e)}')
		print(traceback.format_exc())
	finally:
		plt.close()		
