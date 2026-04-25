from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

class WeatherCard(QWidget):
    def __init__(self, labels):
        super().__init__()

        layout = QVBoxLayout()

        self.day = QLabel(labels['timestamp'][0:10])
        self.time = QLabel(labels['timestamp'][11:-9])

        self.temp = QLabel(f"{labels['temp']}*C")
        self.windSpeed = QLabel(f"{labels['wind_speed']} m/s")

        for widget in [self.day, self.time, self.temp, self.windSpeed]:
            widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(widget)

        self.setLayout(layout)