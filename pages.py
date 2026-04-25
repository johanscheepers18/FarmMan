import PyQt6 as py
import sys
import os
import pyautogui
import json

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QCheckBox, QLabel, QMainWindow, QStatusBar, QToolBar, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QGridLayout, QGroupBox
from widget import WeatherCard
from weather import WeatherAPI

sys.setrecursionlimit(2000)

class DashBoardWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.weatherData = WeatherAPI()

        data = []

        screenHeight, screenWidth = pyautogui.size()

        layout = QGridLayout()

        layout.addWidget(QPushButton("Button (0, 0)"), 0, 0)
        layout.addWidget(QPushButton("Button (0, 1)"), 0, 1)
        layout.addWidget(QPushButton("Button (1, 0)"), 0, 2)

        # weather widget
        weatherBox = QGroupBox("Weather")
        weatherBox.setFixedHeight(int(screenHeight*0.1))

        self.weatherBoxLayout = QHBoxLayout()
        weatherBox.setLayout(self.weatherBoxLayout)

        layout.addWidget(weatherBox, 1, 0, 1, 3)

 
        self.setLayout(layout)

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
