import PyQt6 as py
import sys
import os
import pyautogui
import json
from pathlib import Path

import time

from PyQt6.QtCore import QSize, Qt, QUrl, QTimer, pyqtSignal
from PyQt6.QtWidgets import QLabel, QMainWindow, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QGridLayout, QGroupBox, QLineEdit
from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEngineDownloadRequest
from PyQt6.QtWebEngineWidgets import QWebEngineView

from map import GenerateMap
from hub import signal


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

        self.fieldsView = QWidget()
        self.fieldsView.setObjectName("Fields View")

        self.fieldsViewLayout = QVBoxLayout()
        self.fieldsViewLayout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)

        self.layout.addWidget(self.fieldNavBarWidget)
        self.layout.addWidget(self.fieldsView)

        self.setLayout(self.layout)
        self.UpdateFieldCards()

    def UpdateFieldCards(self):
        try: 
            with open("fieldData.json", 'r') as f:
                self.fieldData = json.load(f)

        except FileNotFoundError:
            return
        
        while self.fieldsViewLayout.count():
            fields = self.fieldsViewLayout.takeAt(0)
            widget = fields.widget()

            if widget is not None:
                widget.deleteLater()

        for field in range(len(self.fieldData[0])):
            self.fieldsViewLayout.addWidget(FieldCard(self.fieldData[0][field]))
            print(range(len(self.fieldData)))

    def displayAddWindow(self):
        self.addWindow = AddFieldWindow()

        self.addWindow.show() 

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

            fieldNameLabel = QLabel("Field Name: ")
            fieldOptionsLayout.addWidget(fieldNameLabel)
            self.fieldName = QLineEdit()
            fieldOptionsLayout.addWidget(self.fieldName)

            confirmButton = QPushButton("Confirm Add")
            fieldOptionsLayout.addWidget(confirmButton)
            confirmButton.clicked.connect(lambda: mapWidget.AddField(self.fieldName.text()))

            self.addLayout.addWidget(mapWidget)
            self.addLayout.addWidget(fieldOptions)


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

        time.sleep(2)

        os.remove(self.tempPath)

        signal.fieldAdded.emit()

        print("DATA PAGES>PY")