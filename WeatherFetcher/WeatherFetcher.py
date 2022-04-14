import pandas as pd
from datetime import datetime
from meteostat import Point, Daily


class WeatherFetcher:
    def __init__(self, data, start_date):
        self.data = data
        self.start_date = datetime(2000, 1, 1)

    def get_weather(self):

        def get_stop_date(row):
            """Determine when to stop pulling weather data from the year the 
            wine was bottled"""
            return datetime(row['year'], 12, 31)

        def query_weather(row):
            """Query with lat/long coordinates and get daily data"""
            
            # Set time period
            start = self.start_date
            end = row['weather_end_date']

            # Create Point for provided coordinates
            weather_point = Point(row['lat'], row['long'], 70)

            # Get daily data for 2018
            data = Daily(weather_point, start, end)
            self.weather_data = data.fetch()

        # Run the functions on every row in the provided database
        self.data['weather_end_date'] = self.data.apply(get_stop_date, axis = 1)
        self.data['weather_data'] = self.data.apply(query_weather, axis = 1)
