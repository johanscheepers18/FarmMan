import PyQt6 as py
import sys
import os

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QCheckBox, QMainWindow, QStatusBar, QToolBar, QPushButton, QHBoxLayout, QVBoxLayout, QWidget
from pages import DashBoardWidget
from fields import FieldsWidget
from map import MapCard
from db import Database, fullFilePath


file_path = os.path.dirname(os.path.abspath(__file__))

stylePath = os.path.join(file_path, "StyleSheet.qss")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        if not os.path.exists(fullFilePath):
             Database()
             print("DB Created")
        self.setWindowTitle("FarmMan")

        self.windStates = {"DASHBOARD" : True, "EQUIPMENT" : False, "FIELDS" : False, "MAP": False, "AUDIT TRAIL": False}

        mainwindow = QWidget()
        self.setCentralWidget(mainwindow)

        self.mainLayout = QVBoxLayout(mainwindow)

        self.navbarWidget = QWidget()
        self.navbarWidget.setObjectName("navbar")

        self.navbarWidget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.navbar = QHBoxLayout(self.navbarWidget)
        self.navbar.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        
        self.dashboardButton = QPushButton("DASHBOARD")
        self.navbar.addWidget(self.dashboardButton)

        # DASHBOARD LAYOUT THAT GOES BELOW THE NAVBAR.
        self.dashboardWidget = DashBoardWidget()
        self.mapCardView = MapCard()
        self.fieldsWidget = FieldsWidget()

        self.mainLayout.addWidget(self.navbarWidget)
        self.mainLayout.addWidget(self.dashboardWidget)
        self.mainLayout.addWidget(self.fieldsWidget)
        self.fieldsWidget.setVisible(False)
        self.mainLayout.addStretch()

        self.showMaximized()

            


def load_styles(app):
        try:
            with open(stylePath, "r") as f:
                style = f.read()
                app.setStyleSheet(style)

        except FileNotFoundError:
             print(f"Error: Could not find {stylePath}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    windowState = True

    load_styles(app)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
