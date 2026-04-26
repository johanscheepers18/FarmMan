import PyQt6 as py
import sys
import os
import pyautogui
import json
from pathlib import Path

import time

from PyQt6.QtCore import QSize, Qt, QUrl, QTimer
from PyQt6.QtWidgets import QLabel, QMainWindow, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QGridLayout, QGroupBox, QLineEdit
from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEngineDownloadRequest
from PyQt6.QtWebEngineWidgets import QWebEngineView

from widget import WeatherCard
from weather import WeatherAPI
from map import MapCard
from hub import signal

sys.setrecursionlimit(2000)
screenWidth, screenHeight = pyautogui.size()

class DashBoardWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.weatherData = WeatherAPI()

        layout = QGridLayout()

        mapBox = QGroupBox("Map")
        mapBox.setFixedHeight(int(screenHeight*0.6))
        print(screenHeight)
        print(screenHeight*0.5)

        self.mapBoxLayout = QHBoxLayout()
        mapBox.setLayout(self.mapBoxLayout)
        
        layout.addWidget(mapBox, 0, 0, 1, 2)

        self.DisplayMap()

        signal.fieldAdded.connect(self.DisplayMap)

        # weather widget
        weatherBox = QGroupBox("Weather")
        weatherBox.setFixedHeight(int(screenHeight*0.2))

        self.weatherBoxLayout = QHBoxLayout()
        weatherBox.setLayout(self.weatherBoxLayout)

        layout.addWidget(weatherBox, 1, 0, 1, 3)

 
        self.setLayout(layout)
        self.UpdateWeatherCards()

        # print(self.liveData)
        self.weatherData.triggerUpdate.connect(self.UpdateWeatherCards)

    def UpdateWeatherCards(self):
        print(">>> SIGNAL RECEIVED! UPDATING UI...")
        try:
            with open("weatherData.json", 'r') as f:
                self.liveData = json.load(f)

        except (FileNotFoundError, json.JSONDecodeError):
            print("Waiting for JSON file to be created...")

        while self.weatherBoxLayout.count():
            item = self.weatherBoxLayout.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        for timeStamp in range(len(self.liveData[0])):
            self.weatherBoxLayout.addWidget(WeatherCard(self.liveData[0][timeStamp]))
            print(range(len(self.liveData)))

    def DisplayMap(self):
        if hasattr(self, 'mapCard') and self.mapCard is not None:
            self.mapBoxLayout.removeWidget(self.mapCard)
            self.mapCard.hide()
            self.mapCard.deleteLater()

        self.mapCard = MapCard()
        # layout.addWidget(mapCard, 0, 0, 1, 2)
        self.mapBoxLayout.addWidget(self.mapCard)

        print("windowUpdated")

