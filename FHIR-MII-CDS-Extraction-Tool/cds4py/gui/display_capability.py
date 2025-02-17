from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QProgressBar, QScrollArea, QLabel, QMessageBox


class CapabilityDisplayWidget(QWidget):
    back_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.request_back)
        self.layout.addWidget(self.back_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 10)
        self.layout.addWidget(self.progress_bar)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area_widget = QWidget()
        self.scroll_area_layout = QVBoxLayout(self.scroll_area_widget)
        self.scroll_area.setWidget(self.scroll_area_widget)
        self.layout.addWidget(self.scroll_area)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def display_capabilities(self, capabilities):
        # Clear previous elements
        for i in reversed(range(self.scroll_area_layout.count())):
            widget_to_remove = self.scroll_area_layout.itemAt(i).widget()
            self.scroll_area_layout.removeWidget(widget_to_remove)
            widget_to_remove.setParent(None)

        # Add each capability as a label in the scrollable area
        for capability in capabilities:
            label = QLabel(capability)
            self.scroll_area_layout.addWidget(label)

    def request_back(self):
        self.back_requested.emit()

    def display_error(self, message):
        QMessageBox.critical(self, "Error", message)
        self.progress_bar.reset()
