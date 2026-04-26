from PyQt6.QtCore import QObject, pyqtSignal

class Comm(QObject):

    fieldAdded = pyqtSignal()

signal = Comm()