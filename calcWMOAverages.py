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


dfResults = pd.DataFrame()

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
		#print(dfAll)

		my_colors = [(100/255, 100/255, 255/255),(140/255, 140/255, 255/255),(180/255, 180/255, 255/255),(220/255, 220/255, 255/255),(100/255, 100/255, 100/255),(150/255, 150/255, 150/255)]

		# line plot temperature with WMO averages
		plot1 = pd.pivot_table(dfAll.reset_index(),
		               index='Month', columns='Period', values='Air temperature 2m, deg C, monthly average'
		              ).plot.line(title=station, color=my_colors)
		plt.ylabel('Air temperature 2m, deg C, monthly average')
		plt.savefig('plotWMOline' + sanitize(station) + '_temperature.pdf')

		# line plot precipitation with WMO averages
		# filter  / split into WMO periods and recent year
		plot2 = pd.pivot_table(dfAll.reset_index(),
		               index='Month', columns='Period', values='Precipition, m, monthly total'
		              ).plot.line(title=station, color=my_colors)
		plt.ylabel('Precipition, m, monthly total')
		plt.savefig('plotWMOline' + sanitize(station) + '_precipitation.pdf')


		# line plot difference from WMO averages in same units
		dfWMOPrecipitation1 = pd.pivot_table(dfAll.loc[(dfAll['Period'] == '1961-1990')].reset_index(), index='Month', columns='Period', values='Precipition, m, monthly total')
		dfWMOPrecipitation2 = pd.pivot_table(dfAll.loc[(dfAll['Period'] == '1991-2020')].reset_index(), index='Month', columns='Period', values='Precipition, m, monthly total')
		dfWMOTemperature1 = pd.pivot_table(dfAll.loc[(dfAll['Period'] == '1961-1990')].reset_index(), index='Month', columns='Period', values='Air temperature 2m, deg C, monthly average')
		dfWMOTemperature2 = pd.pivot_table(dfAll.loc[(dfAll['Period'] == '1991-2020')].reset_index(), index='Month', columns='Period', values='Air temperature 2m, deg C, monthly average')
		dfAll = dfAll.loc[(dfAll['Period'] != '1961-1990')]
		dfAll = dfAll.loc[(dfAll['Period'] != '1991-2020')]

		periods = dfAll.Period.unique()
				
		for period in periods:
			dfPeriodTemp = pd.pivot_table(dfAll.loc[(dfAll['Period'] == period)].reset_index(), index='Month', columns='Period', values='Air temperature 2m, deg C, monthly average')
			dfPeriodPrec = pd.pivot_table(dfAll.loc[(dfAll['Period'] == period)].reset_index(), index='Month', columns='Period', values='Precipition, m, monthly total')
			#print(dfPeriodTemp)
			#print(dfWMOTemperature1)
			#print(dfWMOTemperature2)
			dfMergedTemp = pd.merge(dfWMOTemperature1, dfPeriodTemp, on='Month')
			dfMergedTemp = dfMergedTemp.merge(dfWMOTemperature2, on='Month')
			dfMergedPrec = pd.merge(dfWMOPrecipitation1, dfPeriodPrec, on='Month')
			dfMergedPrec = dfMergedPrec.merge(dfWMOPrecipitation2, on='Month')
			#print(dfMerged)
			dfMergedTemp['WMO1DiffTemp'] = dfMergedTemp[period] - dfMergedTemp['1961-1990']
			dfMergedTemp['WMO2DiffTemp'] = dfMergedTemp[period] - dfMergedTemp['1991-2020']
			dfMergedPrec['WMO1DiffPrec'] = dfMergedPrec[period] - dfMergedPrec['1961-1990']
			dfMergedPrec['WMO2DiffPrec'] = dfMergedPrec[period] - dfMergedPrec['1991-2020']
			dfBothMerged = pd.merge(dfMergedTemp, dfMergedPrec, on='Month')
			dfBothMerged['Year'] = period
			dfBothMerged['Station'] = station
			#print(dfBothMerged)
			dfResults = pd.concat([dfResults, dfBothMerged])

		#print(dfResults)
#		plot2 = pd.pivot_table(dfAll.reset_index(),
#		               index='Month', columns='Period', values='Precipition, m, monthly total'
#		              ).plot.line(title=station, color=my_colors)
#		plt.ylabel('Precipition, m, monthly total')
#		plt.savefig('plotWMOline' + sanitize(station) + '_precipitation.pdf')

	except Exception as e:
		print(f'Error plotting this station, continuing: {str(e)}')
		print(traceback.format_exc())
	finally:
		plt.close()		
print(dfResults)
dfResults.to_csv('stations_wmo_diff_monthly.csv')
