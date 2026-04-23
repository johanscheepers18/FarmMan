import PyQt6 as py
import sys
import os

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QCheckBox, QLabel, QMainWindow, QStatusBar, QToolBar, QPushButton, QHBoxLayout, QVBoxLayout, QWidget
from pages import DashBoardWidget

file_path = os.path.dirname(os.path.abspath(__file__))

stylePath = os.path.join(file_path, "StyleSheet.qss")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FarmMan")

        self.windStates = {"DASHBOARD" : True, "EQUIPMENT" : False, "FIELD RECORDS" : False, "MAP": False, "AUDIT TRAIL": False}

        mainwindow = QWidget()
        self.setCentralWidget(mainwindow)

        mainLayout = QVBoxLayout(mainwindow)

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

        self.fieldrecordsButton = QPushButton("FIELD RECORDS")
        self.fieldrecordsButton.clicked.connect(lambda:self.windowState())
        self.navbar.addWidget(self.fieldrecordsButton)

        self.mapButton = QPushButton("MAP")
        self.mapButton.clicked.connect(lambda:self.windowState())
        self.navbar.addWidget(self.mapButton)

        self.audittrailButton = QPushButton("AUDIT TRAIL")
        self.audittrailButton.clicked.connect(lambda:self.windowState())
        self.navbar.addWidget(self.audittrailButton)

        # DASHBOARD LAYOUT THAT GOES BELOW THE NAVBAR.
        self.dashboardWidget = DashBoardWidget()

        mainLayout.addWidget(self.navbarWidget)
        mainLayout.addWidget(self.dashboardWidget)
        mainLayout.addStretch()

        self.showMaximized()


    def windowState(self):
        button = self.sender()
        
        # SETS ALL KEY/VALUE PAIRS IN WINDSTATES DICTIONARY TO FALSE
        # SETS THE VISIBILITY OF ALL THE MAIN BODY WIDGETS TO FALSE
        for self.key in self.windStates:
                self.windStates[self.key] = False
                self.dashboardWidget.setVisible(self.windStates["DASHBOARD"])

        # MAKES THE DASHBOARD WIDGET VISIBLE
        if (button == self.dashboardButton):
            self.windStates["DASHBOARD"] = True
            print(f"DASHBOARD: {self.windStates}")
            self.dashboardWidget.setVisible(self.windStates["DASHBOARD"])

        #MAKES THE QUIPMENT WIDGET VISIBLE    
        elif (button == self.equipmentButton):
            self.windStates["EQUIPMENT"] = True
            print(f"EQUIPMENT: {self.windStates}")

        # MAKES THE FIELD RECORDS WIDGET VISIBLE
        elif (button == self.fieldrecordsButton):
            self.windStates["FIELD RECORDS"] = True
            print(f"FIELD RECORDS: {self.windStates}")

        # MAKES THE MAP WIDGET VISIBLE
        elif (button == self.mapButton):
            self.windStates["MAP"] = True
            print(f"MAP: {self.windStates}")

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

    load_styles(app)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
