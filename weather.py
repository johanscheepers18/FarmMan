from fake_useragent import UserAgent
import json
from email.utils import format_datetime
import time
import requests
import os
from threading import Timer

from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QThread

from datetime import date, datetime
from map import GenerateMap

# Using the YR Weather API for real-time location based weather data on the dashboard
# API DOCS: https://developer.yr.no/doc/locationforecast/HowTO/

class WeatherAPI(QObject):

    triggerUpdate = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.CallApi()

    def CallApi(self):
        sitename = "https://github.com/johanscheepers18/FarmMan"

        coDataFile = os.path.join(GenerateMap.userDataPath, GenerateMap.userDataFile)

        lat, lon = -34.0320, 24.9176
        if os.path.exists(coDataFile):
            with open(coDataFile, 'r') as f:
                coord = json.load(f)
            for feature in coord["features"]:
                print(feature)
                if feature["geometry"]["type"] == "Point":
                    lon = round(feature["geometry"]["coordinates"][0], 4)
                    lat = round(feature["geometry"]["coordinates"][1], 4)
                    break

        print(f'lat{lat}, lon{lon}')

        ua = UserAgent()
        currentTime = datetime.now().astimezone()
        rfc = format_datetime(currentTime)
        headers = {'User-Agent': ua.random + sitename, 'Date': rfc}

        params = {
            'lat': lat,
            'lon': lon,
            'altitude': 65
        }

        url = "https://api.met.no/weatherapi/locationforecast/2.0/"

        try:
            response = requests.get(url, params=params ,headers=headers)

            if response.status_code == 200:
                data = response.json()
                self.DataSort(data)
                print("Success! Data retrieved. called api.")
            elif response.status_code == 403:
                print("Error 403: Your User-Agent was rejected. Double-check your format.")
            else:
                print(f"Error: Received status code {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Connection error: {e}")

        # Timer for when the data should be updated: currently it's 10min(600sec) intervals.
        
        thread = Timer(600.0, self.CallApi)
        thread.daemon = True
        thread.start()

    def ConvertTime(self, timestamp):
        utc = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        local = utc.astimezone()

        return local


    def DataSort(self, data):
        timestamps = data['properties']['timeseries']
        counter = 0

        self.dataArray = []

        # for loop used to loop through json data for each timestamp
        # range(len(timestamps)-1): Is used to check the length of the dictionary, 
        # I minus one (-1) since the last key:value pair has no condition code and is too far in the future.
        for i in range(len(timestamps)-1):
            currentPoint = data['properties']['timeseries'][counter]

            # Variable to store the timestamp of each key:value pair
            # apiTime = currentPoint['time']
            apiTime = self.ConvertTime(currentPoint['time'])
            # Variable that stores the temperature
            temp = currentPoint['data']['instant']['details']['air_temperature']
            # Variable that stores the windspeed
            wind = currentPoint['data']['instant']['details']['wind_speed']

            # if statement to check if the key:value pair has the condition code (clear sky, cloudy sky etc.) for the next hour ['next_1_hours'],
            # if it doesn't then it should use the ['next_6_hours'] value.
            if 'next_1_hours' in currentPoint['data']:
                symbol = currentPoint['data']['next_1_hours']['summary']['symbol_code']

            else:
                symbol = currentPoint['data']['next_6_hours']['summary']['symbol_code']

            # This is just used as debugging to check if my code is working correctly. 
            # This will be switched in the future for a r,w function to create a .json file,
            # FarmMan will use this file to update the weather data that is displayed on the dashboard.
            # print(f"Time Stamp: {apiTime}")
            # print(f"Current Temperature: {temp}°C")
            # print(f"Wind Speed: {wind} m/s")
            # print(f"Condition Code: {symbol}")

            timeDict = {'timestamp': str(apiTime), 'temp': temp, 'wind_speed': wind, 'condition': symbol}
            self.dataArray.append(timeDict)
            counter += 1

        self.completeData = self.OrganizeData(self.dataArray)

        with open('weatherData.json', 'w') as f:
            json.dump(self.completeData, f, indent=4)

        self.triggerUpdate.emit()

    # Function to organize data that had been received by the API call.
    def OrganizeData(self, dataArray):
        # Array of arrays that contains the final organized data, sorted by date.
        organizedData = []

        # Data for date X gets stored in this as array of dictionaries.
        dayData = []
        # Date that should be used to compare the dataArray 'timestamp' key/value pair.
        # Default date: System current date.
        compDate = str(date.today())
        # For loop that looks at all pointer dictionaries in the dataArray
        for pointer in dataArray:
            # Variable that stores the pointers date to be compared.
            # Date is stored as the value of timestamp. within the range of 0 - 10.
            # Date is stored as yyyy-mm-dd
            pointerDate = pointer['timestamp'][0:10]
            
            # Makes sure the pointer is for the correct date
            if pointerDate == compDate:
                dayData.append(pointer)

            # Finalize previous day's data and intialize the following day's data.
            else:
                organizedData.append(dayData)
                dayData = []

                compDate = pointerDate
                dayData.append(pointer)

        return organizedData

    