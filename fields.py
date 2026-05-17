import PyQt6 as py
import sys
import os
import pyautogui
import json
from pathlib import Path
from db import Database

import time

from PyQt6.QtCore import QSize, Qt, QUrl, QTimer, pyqtSignal
from PyQt6.QtWidgets import QLabel, QMainWindow, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QGridLayout, QGroupBox, QLineEdit, QScrollArea
from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEngineDownloadRequest
from PyQt6.QtWebEngineWidgets import QWebEngineView

from map import GenerateMap
from hub import signal
from widget import FieldCard


screenWidth, screenHeight = pyautogui.size()
class FieldsWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.mainwindow = QWidget()

        self.layout = QVBoxLayout(self.mainwindow)

        self.fieldNavBarWidget = QWidget()
        self.fieldNavBarWidget.setObjectName("Field Options")

        self.fieldNavBarWidget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.fieldNavBar = QHBoxLayout(self.fieldNavBarWidget)
        self.fieldNavBar.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self.addFieldButton = QPushButton("Add Field")
        self.addFieldButton.clicked.connect(self.displayAddWindow)
        self.fieldNavBar.addWidget(self.addFieldButton)

        self.fieldScroll = QScrollArea()

        self.fieldsView = QWidget()
        self.fieldsView.setObjectName("Fields View")

        self.fieldsViewLayout = QVBoxLayout(self.fieldsView)
        self.fieldsViewLayout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)

        self.fieldScroll.setFixedHeight(int(screenHeight*0.5))
        self.fieldScroll.setFixedWidth(int(screenWidth*0.42))
        self.fieldScroll.setWidget(self.fieldsView)
        self.fieldScroll.setWidgetResizable(True)

        self.layout.addWidget(self.fieldNavBarWidget)
        self.layout.addWidget(self.fieldScroll)
        # self.fieldsViewLayout.addWidget(FieldCard())

        self.setLayout(self.layout)
        self.UpdateFieldCards()

        signal.fieldAdded.connect(self.UpdateFieldCards)

    def UpdateFieldCards(self):
        try: 
            with open(os.path.join(AddMap.userDataPath, AddMap.userDataFile), 'r') as f:
                self.fieldData = json.load(f)

            while self.fieldsViewLayout.count():
                fields = self.fieldsViewLayout.takeAt(0)
                widget = fields.widget()

                if widget is not None:
                    widget.deleteLater()

            for field in self.fieldData["features"]:
                if field["geometry"]["type"] == "Polygon":
                    self.fieldsViewLayout.addWidget(FieldCard(field["geometry"]["coordinates"][0], field["properties"]["name"]))

        except FileNotFoundError:
            pass

    def displayAddWindow(self):
        self.addWindow = AddFieldWindow()

        self.addWindow.show()

#     ///////////////////////////////////////////////////////////////////////////////////
#    ////////////////////////                                 //////////////////////////
#   ////////////////////////    DATA LAYER FOR FIELDS TAB    //////////////////////////
#  ////////////////////////                                 //////////////////////////
# ///////////////////////////////////////////////////////////////////////////////////

class AddFieldWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            mapWidget = AddMap()

            print("ADDFIELD WINDOW")
            self.mainContent = QWidget()
            self.setCentralWidget(self.mainContent)

            self.addLayout = QHBoxLayout(self.mainContent)

            fieldOptions = QWidget()
            fieldOptionsLayout = QVBoxLayout(fieldOptions)

            self.fieldNameLayout = QHBoxLayout()
            fieldNameLabel = QLabel("Field Name: ")
            self.fieldName = QLineEdit()
            self.fieldNameLayout.addWidget(fieldNameLabel)
            self.fieldNameLayout.addWidget(self.fieldName)
            fieldOptionsLayout.addLayout(self.fieldNameLayout)

            fieldCropLayout = QHBoxLayout()
            fieldCrop = QLabel("Current Crop: ")
            self.fieldCropText = QLineEdit()
            fieldCropLayout.addWidget(fieldCrop)
            fieldCropLayout.addWidget(self.fieldCropText)
            fieldOptionsLayout.addLayout(fieldCropLayout)


            fieldStatusLayout = QHBoxLayout()
            fieldStatus = QLabel("Current Field Status: ")
            self.fieldStatusText = QLineEdit()
            fieldStatusLayout.addWidget(fieldStatus)
            fieldStatusLayout.addWidget(self.fieldStatusText)

            confirmButton = QPushButton("Confirm Add")
            fieldOptionsLayout.addWidget(confirmButton)
            confirmButton.clicked.connect(lambda: mapWidget.AddField(self.fieldName.text()))

            self.addLayout.addWidget(mapWidget)
            self.addLayout.addWidget(fieldOptions)

            signal.fieldAdded.connect(self.CloseAfterComp)

        def CloseAfterComp(self):
            self.close()


class AddMap(QWidget):
    userDataPath = Path.home() / "Documents" / "FarmMan"
    userDataFile = "userMapData.geojson"
    fullSavePath = os.path.join(str(userDataPath), userDataFile)
    tempFile = "temp_data.geojson"
    tempPath = os.path.join(str(userDataPath), tempFile)
    def __init__(self):
        super().__init__()
        self.generatedMap = GenerateMap(False)

        layout = QVBoxLayout(self)

        self.mapView = QWebEngineView()
        # self.mapView.setFixedHeight(int(screenHeight*0.6))
        self.mapView.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)

        layout.addWidget(self.mapView)
        self.setLayout(layout)
        print(self.generatedMap.html_file)

        self.fieldName = "unknown field"

        self.mapView.load(QUrl.fromLocalFile(self.generatedMap.html_file))

        try:
            self.mapView.page().profile().downloadRequested.disconnect()
        except TypeError:
            pass

        self.mapView.page().profile().downloadRequested.connect(self.SaveGeoDataPages)

    def AddField(self, fieldName):
        self.fieldName = fieldName

        jsTrigger = """
                    var buttons = document.querySelectorAll('a, button');
                    var exportBtn = Array.from(buttons).find(el => el.textContent.trim() === 'Export');
                    
                    if (exportBtn) {
                        exportBtn.click();
                    } else {
                        console.error('Export button not found on map');
                    }
                    """
        self.mapView.page().runJavaScript(jsTrigger)

    def SaveGeoDataPages(self, download: QWebEngineDownloadRequest):

        download.setDownloadDirectory(str(self.userDataPath))
        download.setDownloadFileName(self.tempFile)

        download.accept()

        download.isFinishedChanged.connect(lambda: self.DownloadFinishedPages(download))

        print(f"Data saved to: {self.fullSavePath}")

    def DownloadFinishedPages(self, download: QWebEngineDownloadRequest):
        if download.isFinished():
            QTimer.singleShot(500, self.AddTempDataPages)

    def AddTempDataPages(self):

        if os.path.exists(self.fullSavePath):
            with open(self.fullSavePath, 'r') as f:
                data = json.load(f)

        else:
            data = {"type": "FeatureCollection", "features": []}

        with open(self.tempPath, 'r') as f:
            newData = json.load(f)
        
        if newData["features"]:
            newField = newData["features"][-1]
            if "properties" not in newField:
                newField["properties"] = {}

            newField["properties"]["name"] = self.fieldName
            data["features"].append(newField)

        with open(self.fullSavePath, "w") as f:
            json.dump(data, f, indent=4)

        Database.AddFieldDB(newField["properties"]["name"], "", "", "", str(newField["geometry"]["coordinates"][0]))

        time.sleep(1)

        os.remove(self.tempPath)

        signal.fieldAdded.emit()

        print("DATA PAGES>PY")
