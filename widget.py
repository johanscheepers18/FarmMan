from PyQt6.QtWidgets import QWidget, QMainWindow, QVBoxLayout, QLabel, QGroupBox, QHBoxLayout, QPushButton
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from PyQt6.QtWebEngineWidgets import QWebEngineView

import pyautogui
import numpy as np
import pandas as pd
import geopandas as gpd
import folium as fol
import json
from shapely import Polygon
from shapely.geometry import shape
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


from db import Database

screenWidth, screenHeight = pyautogui.size()

class WeatherCard(QWidget):
    def __init__(self, labels):
        super().__init__()

        layout = QVBoxLayout()

        self.day = QLabel(labels['timestamp'][0:10])
        self.time = QLabel(labels['timestamp'][11:-9])

        self.temp = QLabel(f"{labels['temp']}*C")
        self.windSpeed = QLabel(f"{labels['wind_speed']} m/s")

        for widget in [self.day, self.time, self.temp, self.windSpeed]:
            print(widget)
            widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(widget)

        self.setLayout(layout)

class FieldCard(QGroupBox):
    def __init__(self, fieldCoords, fieldName):
        super().__init__()
        features = []
        for row in Database.FetchFields():
            print(row)
            fid, name, crop, status, area, geoStr = row
            print(geoStr)
            geo = json.loads(geoStr)
            features.append({"id": fid, "name": name, "crop": crop, "status": status, "geometry": geo})
        
        print(f"FIELDCARD: {features}")
        self.fieldbackup = fieldCoords
        for feature in features:
            self.fieldName = feature["name"]
            if self.fieldName == fieldName:
                self.field = feature["geometry"]
        print(self.field)
        polygon = Polygon(self.field)

        self.gdf = gpd.GeoDataFrame(index=[0], crs='epsg:4326', geometry=[polygon])
        self.reproject = self.gdf.to_crs(self.gdf.estimate_utm_crs())

        area = str(np.round(self.reproject.geometry.area.iloc[0] / 10000, 2))
        print(area)
        # Card to store field data
        
        self.setFixedWidth(int(screenWidth*0.4))
        self.setFixedHeight(int(screenHeight*0.1))

        self.fieldCardLayout = QHBoxLayout()
        self.setLayout(self.fieldCardLayout)

        self.fig = Figure(figsize=(1,1), dpi=100)
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111)

        self.ax.axis('off')

        self.fieldInfo = QGroupBox()
        self.fieldInfoLayout = QVBoxLayout(self.fieldInfo)
        self.fieldInfo.setFixedWidth(int(screenWidth*0.3))

        self.fieldName = QLabel(f"Field Name: {fieldName}")
        self.fieldArea = QLabel(f"Field Area: {area}")
        self.viewDetails = QPushButton("View Field")
        self.viewDetails.clicked.connect(lambda: self.displayFieldInfo(fieldName))
        self.fieldInfoLayout.addWidget(self.fieldName)
        self.fieldInfoLayout.addWidget(self.fieldArea)
        self.fieldInfoLayout.addWidget(self.viewDetails)

        self.fieldCardLayout.addWidget(self.canvas)
        self.fieldCardLayout.addWidget(self.fieldInfo)

        self.CalPoly()


    def CalPoly(self):
        
        # polygon = Polygon(self.field)
        # self.gdf = gpd.GeoDataFrame(index=[0], crs='epsg:4326', geometry=[polygon])
        # metric = self.gdf.to_crs(epsg=32733)
        # self.gdf['area_m2'] = metric.geometry.area

        self.gdf.plot(ax=self.ax, color='skyblue', edgecolor='black')
        self.canvas.draw()

    def displayFieldInfo(self, fieldName):
        self.window = FieldInfoWindow(fieldName)

        self.window.show()

class FieldInfoWindow(QMainWindow):
        
        def __init__(self, fieldName):
            super().__init__()
            self.mainWindow = QWidget()
            self.setCentralWidget(self.mainWindow)
            self.mainLayout = QVBoxLayout(self.mainWindow)

            fieldInfo = Database.FetchInField(fieldName)

            fieldTestInfo = QLabel(str(fieldInfo[0][0]))

            self.mainLayout.addWidget(fieldTestInfo)