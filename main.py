import PyQt6 as py
import sys
import os

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QCheckBox, QLabel, QMainWindow, QStatusBar, QToolBar, QPushButton, QHBoxLayout, QVBoxLayout, QWidget
from pages import DashBoardWidget
from fields import FieldsWidget
from map import MapCard


file_path = os.path.dirname(os.path.abspath(__file__))

stylePath = os.path.join(file_path, "StyleSheet.qss")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
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
        self.dashboardButton.clicked.connect(lambda:self.windowState())
        self.navbar.addWidget(self.dashboardButton)

        self.equipmentButton = QPushButton("EQUIPMENT")
        self.equipmentButton.clicked.connect(lambda:self.windowState())
        self.navbar.addWidget(self.equipmentButton)

        self.fields = QPushButton("FIELDS")
        self.fields.clicked.connect(lambda:self.windowState())
        self.navbar.addWidget(self.fields)

        self.mapButton = QPushButton("MAP")
        self.mapButton.clicked.connect(lambda:self.windowState())
        self.navbar.addWidget(self.mapButton)

        self.audittrailButton = QPushButton("AUDIT TRAIL")
        self.audittrailButton.clicked.connect(lambda:self.windowState())
        self.navbar.addWidget(self.audittrailButton)

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


    def windowState(self):
        button = self.sender()
        
        # SETS ALL KEY/VALUE PAIRS IN WINDSTATES DICTIONARY TO FALSE
        # SETS THE VISIBILITY OF ALL THE MAIN BODY WIDGETS TO FALSE
        for self.key in self.windStates:
                self.windStates[self.key] = False
                
        # MAKES THE DASHBOARD WIDGET VISIBLE
        if (button == self.dashboardButton):
            self.windStates["DASHBOARD"] = True
            self.fieldsWidget.setVisible(self.windStates["FIELDS"])
            self.dashboardWidget.setVisible(self.windStates["DASHBOARD"])

        #MAKES THE QUIPMENT WIDGET VISIBLE    
        elif (button == self.equipmentButton):
            self.windStates["EQUIPMENT"] = True
            print(f"EQUIPMENT: {self.windStates}")

        # MAKES THE FIELD RECORDS WIDGET VISIBLE
        elif (button == self.fields):
            self.windStates["FIELDS"] = True
            self.dashboardWidget.setVisible(self.windStates["DASHBOARD"])
            self.fieldsWidget.setVisible(self.windStates["FIELDS"])

        # MAKES THE MAP WIDGET VISIBLE
        elif (button == self.mapButton):
            self.windStates["MAP"] = True
            self.mapCardView.setVisible(self.windStates["MAP"])

        # MAKES THE AUDIT TRAIL VISIBLE
        elif (button == self.audittrailButton):
            self.windStates["AUDIT TRAIL"] = True
            print(f"AUDIT TRAIL: {self.windStates}")

            


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
