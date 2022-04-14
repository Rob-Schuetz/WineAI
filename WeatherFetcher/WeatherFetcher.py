import pandas as pd
from datetime import datetime
from meteostat import Daily, Stations


class WeatherFetcher:
    def __init__(self, data, start_date):
        self.input = data # pd.DataFrame with the following columns ['Longitude', 'Latitude', 'Vintage Year]
        self.start_date = start_date # How far back to pull historical weather data
        self.daily_weather_data = {} # Dictionary to capture returned weather data frames, shares index with self.input

    def get_weather(self):

        def get_stop_date(row):
            """Determine when to stop pulling weather data from the year the 
            wine was bottled"""
            return datetime(int(row['Vintage Year']), 12, 31)

        def query_weather(row):
            """Query with lat/long coordinates and get daily data"""

            # Set time period
            start = self.start_date
            end = get_stop_date(row)

            # Get the closest weather station
            stations = Stations()
            stations = stations.nearby(row['Latitude'], row['Longitude'])
            station = stations.fetch(1).index.values[0]

            # Get daily data bewtween designated date range
            data = Daily(station, start, end)
            return data.fetch()

        # Run the functions on every row in the provided database
        # self.data['weather_data'] = self.data.apply(query_weather, axis = 1)
        for idx, row in self.input.iterrows():
            self.daily_weather_data[idx] = query_weather(row)

