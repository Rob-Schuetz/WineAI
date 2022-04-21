import pandas as pd
from datetime import datetime
import time
from meteostat import Daily, Stations


class WeatherFetcher:
    def __init__(self, data):
        self.input = data # pd.DataFrame with the following columns ['Longitude', 'Latitude', 'Vintage Year]
        self.daily_weather_data = {} # Dictionary to capture returned complete weather data frames, indexed by {Vintage Year}-{Region}
        self.cleaned_weather_data = {} # Dictionary to capture imputed data
        self.output = {} # Dictionary to capture weather for distinct year-region combinations

    def query_weather(self):

        """
        Query lat/long coordinates to fetch daily data over
        necessary date ranges indicated in unique year-region combinations
        """

        # Iterate through distinct year-region combinations
        yr_df = self.input[['region', 'latitude', 'longitude']].drop_duplicates()
        yr_mins = self.input.groupby(['region'])['vintage'].min()
        yr_maxs = self.input.groupby(['region'])['vintage'].max()
        yr_df = yr_df.merge(yr_mins, left_on='region', right_index=True).rename(columns = {'vintage': 'min_year'})
        yr_df = yr_df.merge(yr_maxs, left_on='region', right_index=True).rename(columns = {'vintage': 'max_year'})
        
        # For each region, query data according to provided year ranges
        for idx, row in yr_df.iterrows():

            # Get the closest weather station
            stations = Stations()
            stations = stations.nearby(row['latitude'], row['longitude'])
            station = stations.fetch(1).index.values[0]

            # Get daily data bewtween designated date range
            start = datetime(int(row['min_year']), 1, 1)
            end = datetime(int(row['max_year']), 12, 31)
            data = Daily(station, start, end)
            
            # Assign regional data to daily_weather_data dict
            self.daily_weather_data[f'{row["region"]}'] = data.fetch()
            
            # Report successful weather data query
            print(f'Data has been pulled for {row["region"]} ({row["min_year"]} - {row["max_year"]})')
        
        print()


    def clean_weather_data(self):
        """
        Clean data according to the following guidelines:
            1. Fill null snow and rain with monthly average / days
            2. Nixing wind direction, wind gust, tsun columns
            3. Convert pressure to ATM
            4. Fill null pressure and wind speeds with monthly averages over all available years
        """

        # Go through each weather location data frame
        for k, v in self.daily_weather_data.items():
            
            # Start timer
            tic = time.perf_counter()

            # Remove superfluous columns
            df = v.drop(columns=['wdir', 'wpgt', 'tsun'])

            # Fill snow NAs
            na_values = {'snow': 0}
            df = df.fillna(value=na_values)

            # Convert pressure to ATM
            df['pres'] = df['pres'] * 0.0009869233 # originally recorded in hPa

            # Fill columns with monthly averages
            def get_monthly_average(row, column, df):
                if pd.notna(row[column]):
                    return row[column]
                months = [x.month for x in df.index.to_list()]
                monthly_data = df.loc[[m == row.name.month for m in months]][column]
                monthly_mean = monthly_data.dropna().mean()
                return monthly_mean

            # For float columns
            float_columns = [d_k for d_k, d_v in df.dtypes.to_dict().items() if d_v == 'float']
            for c in float_columns:
                df[c] = df.apply(get_monthly_average, axis = 1, column = c, df = df)

            # Restrict dates to those occuring during growing season of the provided vintage year
            self.cleaned_weather_data[k] = df.reset_index()

            # Report successful weather data query
            toc = time.perf_counter()
            print(f'Data has been cleaned for {k} in {toc - tic:0.4f} seconds')

        print()

        
    def filter_weather_data(self):

        """
        Once necessary data has been retrieved from the meteostat Daily object 
        and has been properly cleaned, we need to break it into necessary year_region data frames
        """

        # Run the functions on every row in the provided database
        for idx, row in self.input[['region', 'vintage']].drop_duplicates().iterrows():

            # Read in data for the designated region
            region_data = self.cleaned_weather_data[f'{row["region"]}']
            self.output[f'{row["region"]}-{row["vintage"]}'] = region_data.loc[
                (region_data['time'] >= datetime(int(row["vintage"]), 3, 1))
            & 
                (region_data['time'] <= datetime(int(row["vintage"]), 10, 31))
            ].reset_index(drop=True)

            # Report successful filtering 
            print(f'Data filtered for {row["region"]} ({row["vintage"]})')
