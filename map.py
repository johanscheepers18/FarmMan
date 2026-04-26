import folium as fol
from folium.plugins import Draw
import os
from pathlib import Path

import geojson
import json
import time

from PyQt6.QtCore import QSize, Qt, QUrl , QTimer, pyqtSignal
from PyQt6.QtWidgets import QApplication, QCheckBox, QLabel, QMainWindow, QStatusBar, QToolBar, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QGridLayout, QGroupBox
from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEngineDownloadRequest
from PyQt6.QtWebEngineWidgets import QWebEngineView


class GenerateMap():
    userDataPath = Path.home() / "Documents" / "FarmMan"
    userDataFile = "userMapData.geojson"
    html_file = os.path.abspath("testFarm.html")
    def __init__(self, loadData):
        super().__init__()
        self.fullSavePath = os.path.join(str(self.userDataPath), self.userDataFile)

        lat, lon = -34.0320, 24.9176
        if os.path.exists(self.fullSavePath):
            with open(self.fullSavePath, 'r') as f:
                coord = json.load(f)
            for feature in coord["features"]:
                print(feature)
                if feature["geometry"]["type"] == "Point":
                    lon = round(feature["geometry"]["coordinates"][0], 4)
                    lat = round(feature["geometry"]["coordinates"][1], 4)
                    break
        self.map = fol.Map(location=(lat, lon), zoom_start=15, control_scale=True)

        fol.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr="'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'",
            name="Esri.WorldImagery"
            ).add_to(self.map)

        if loadData:
            if Path(self.fullSavePath).exists():
                with open(self.fullSavePath, 'r') as f:
                    self.geoData = geojson.load(f)
            else:
                self.geoData = {"type": "FeatureCollection", "features": []}


            fol.GeoJson(
                self.geoData,
                name="geojson",
                style_function=lambda feature: {
                    "fillColor": "#ffff00",
                    "color": "black",
                    "weight": 2,
                }
            ).add_to(self.map)

            editGroup = fol.FeatureGroup(name = "Editable Data")

            for feature in self.geoData['features']:
                geometry = feature['geometry']
                coords = feature['geometry']['coordinates']

                if geometry == 'Point':
                    # fol.Marker(location=[coords[1], coords[0]]).add_to(editGroup)
                    folCoords = [geometry['coordinates'][1], geometry['coordinates'][0]]
                    fol.marker(location=folCoords).add_to(editGroup)

                elif geometry == 'Polygon':
                    # fol.Polygon(locations=[(p[1], p[0]) for p in coords[0]]).add_to(editGroup)
                    folCoords = [[p[1], p[0]] for p in geometry['coordinates'][0]]

                    fol.Polygon(
                        locations=folCoords,
                        fill=True,
                        color='blue'
                    ).add_to(editGroup)

            editGroup.add_to(self.map)

            draw = Draw(
                export=True,
                filename='userFields.geojson',
                feature_group=editGroup,
                draw_options={
                    'polyline': False,
                    'rectangle': False,
                    'polygon': False,
                    'circle': False,
                    'marker': True,
                    'circlemarker': False,
                },
                edit_options={'edit': True}
            )

            draw.add_to(self.map)

            fol.LayerControl().add_to(self.map)

            self.map.save(self.html_file)

            self.DisableMarker()

        else:
            draw = Draw(
                export=True,
                filename='userFields.geojson',
                draw_options={
                    'polyline': True,
                    'rectangle': True,
                    'polygon': True,
                    'circle': True,
                    'marker': False,
                    'circlemarker': False,
                },
                edit_options={'edit': True}
            )

            draw.add_to(self.map)

            fol.LayerControl().add_to(self.map)

            self.map.save(self.html_file)

            self.DisableMarker()


    def DisableMarker(self):
        map_name = self.map.get_name()
        with open(self.html_file, "a", encoding="utf-8") as f:
            f.write(f"""
        <script>
        (function() {{
            var map = window['{map_name}'];
            if (!map) {{
                setTimeout(arguments.callee, 100);
                return;
            }}

            // Function to hide the marker button
            function hideMarkerButton() {{
                var markerBtn = document.querySelector('a.leaflet-draw-draw-marker');
                if (markerBtn) {{
                    markerBtn.style.display = 'none'; // Using display none is safer than removeChild
                }}
            }}

            // 1. Check on Load: If GeoJSON already contains a marker, hide the button
            map.eachLayer(function(layer) {{
                if (layer instanceof L.Marker) {{
                    hideMarkerButton();
                }}
            }});

            // 2. Check on Draw: Existing logic for manual placement
            map.on('draw:created', function(e) {{
                if (e.layerType === 'marker') {{
                    hideMarkerButton();
                    if (map._drawControl && map._drawControl._toolbars.draw._modes.marker.handler) {{
                        map._drawControl._toolbars.draw._modes.marker.handler.disable();
                    }}
                }}
            }});
        }})();
        </script>
        """)

class MapCard(QWidget):
    userDataPath = Path.home() / "Documents" / "FarmMan"
    userDataFile = "userMapData.geojson"
    fullSavePath = os.path.join(str(userDataPath), userDataFile)
    tempFile = "temp_data.geojson"
    tempPath = os.path.join(str(userDataPath), tempFile)
    def __init__(self):
        super().__init__()
        print("map card")

        self.generatedMap = GenerateMap(True)

        layout = QVBoxLayout(self)

        self.mapView = QWebEngineView()
        self.mapView.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)

        layout.addWidget(self.mapView)
        self.setLayout(layout)
        print(self.generatedMap.html_file)
        self.mapView.load(QUrl.fromLocalFile(self.generatedMap.html_file))

        self.mapView.page().profile().downloadRequested.connect(self.SaveGeoData)

    def SaveGeoData(self, download: QWebEngineDownloadRequest):

        download.setDownloadDirectory(str(self.userDataPath))
        download.setDownloadFileName(self.tempFile)

        download.accept()

        download.isFinishedChanged.connect(lambda: self.DownloadFinished(download))

        print(f"Data saved to: {self.fullSavePath}")

    def DownloadFinished(self, download: QWebEngineDownloadRequest):
        if download.isFinished():
            QTimer.singleShot(500, self.AddTempData)

    def AddTempData(self):
        if os.path.exists(self.fullSavePath):
            with open(self.fullSavePath, 'r') as f:
                data = json.load(f)

        else:
            data = {"type": "FeatureCollection", "features": []}

        with open(self.tempPath, 'r') as f:
            newData = json.load(f)

        data["features"].extend(newData["features"])
        with open(self.fullSavePath, "w") as f:
            json.dump(data, f, indent=4)

        print("DATA MERGED")

    # def LoadGeoData(self):
    #     self.fullSavePath = os.path.join(str(self.userDataPath), self.userDataFile)
    #     if Path(self.fullSavePath).exists():
    #         with open(self.fullSavePath, 'r') as f:
    #             return json.load(f)
        
    #     return {"type": "FeatureCollection", "features": []}

        