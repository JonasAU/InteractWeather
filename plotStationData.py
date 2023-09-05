import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from sanitize_filename import sanitize
import sys

filename = sys.argv[1]
print(filename)
df = pd.read_csv (filename)

years = df.Year.unique()
stations = df.StationName.unique()

#print(years)
#print(stations)

season_dict = {1: 'Winter',
               2: 'Winter',
               3: 'Spring', 
               4: 'Spring',
               5: 'Spring',
               6: 'Summer',
               7: 'Summer',
               8: 'Summer',
               9: 'Fall',
               10: 'Fall',
               11: 'Fall',
               12: 'Winter'}
df['Season'] = df['Month'].apply(lambda x: season_dict[x])

print(df)

for station in stations:
	print(station)
	try:
		dfFilter = df.loc[df['StationName'] == station]
		dfFilter = dfFilter.loc[dfFilter['Year'] >= 2019]

		# recent years temperature
		dfFilter = dfFilter.loc[dfFilter['Air temperature 2m, deg C, monthly average'] != '--']
		plot1 = pd.pivot_table(dfFilter.reset_index(),
		               index='Month', columns='Year', values='Air temperature 2m, deg C, monthly average'
		              ).plot.bar(title=station)
		plt.ylabel('Air temperature 2m, deg C, monthly average')
		plt.savefig('plot' + sanitize(station) + '_temperature.pdf')

		# recent years precipitation
		dfFilter = dfFilter.loc[dfFilter['Precipition, m, monthly total'] != '--']
		plot1 = pd.pivot_table(dfFilter.reset_index(),
		               index='Month', columns='Year', values='Precipition, m, monthly total'
		              ).plot.bar(title=station)
		plt.ylabel('Total precipition / day, m, monthly average')
		plt.savefig('plot' + sanitize(station) + '_precipitation.pdf')

		# timeseries plot all years line
		dfFilter = df.loc[df['StationName'] == station]
		dfFilter = dfFilter.loc[dfFilter['Air temperature 2m, deg C, monthly average'] != '--']
		dfFilter = dfFilter.loc[dfFilter['Precipition, m, monthly total'] != '--']
		print(dfFilter)
		dfSeasonal = dfFilter.copy()
		dfSeasonal['Air temperature 2m, deg C, monthly average'] = pd.to_numeric(dfSeasonal["Air temperature 2m, deg C, monthly average"], downcast="float")
		dfSeasonal['Precipition, m, monthly total'] = pd.to_numeric(dfSeasonal['Precipition, m, monthly total'], downcast="float")
		dfSeasonal['averageTemperature'] = dfSeasonal.groupby(['StationName', 'Year', 'Season'])['Air temperature 2m, deg C, monthly average'].transform(np.mean)
		dfSeasonal['averagePrecipitation'] = dfSeasonal.groupby(['StationName', 'Year', 'Season'])['Precipition, m, monthly total'].transform(np.mean)
		print(dfSeasonal)
		dfSeasonal = dfSeasonal.drop_duplicates(subset=['StationName', 'Year', 'Season', 'averageTemperature', 'averagePrecipitation'])
		print(dfSeasonal)

		pd.pivot_table(dfSeasonal.reset_index(),
		       index='Year', columns="Season", values='averagePrecipitation'
		      ).plot.line(title=station)
		plt.ylabel('Precipitation')

		locator = matplotlib.ticker.MultipleLocator(10)
		plt.gca().xaxis.set_major_locator(locator)
		formatter = matplotlib.ticker.StrMethodFormatter("{x:.0f}")
		plt.gca().xaxis.set_major_formatter(formatter)

		plt.savefig('plotLine' + sanitize(station) + '_precipitation.pdf')

		pd.pivot_table(dfSeasonal.reset_index(),
		       index='Year', columns="Season", values='averageTemperature'
		      ).plot.line(title=station)
		plt.ylabel('Temperature')

		locator = matplotlib.ticker.MultipleLocator(10)
		plt.gca().xaxis.set_major_locator(locator)
		formatter = matplotlib.ticker.StrMethodFormatter("{x:.0f}")
		plt.gca().xaxis.set_major_formatter(formatter)

		plt.savefig('plotLine' + sanitize(station) + '_temperature.pdf')

	except Exception as e:
		print(f'Error plotting this station, continuing: {str(e)}')
	finally:
		plt.close()		
