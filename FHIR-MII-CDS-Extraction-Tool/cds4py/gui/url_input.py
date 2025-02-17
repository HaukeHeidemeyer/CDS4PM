from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFileDialog
import json
import logging

logger = logging.getLogger(__name__)

class URLInputWidget(QWidget):
    url_submitted = pyqtSignal(str)
    show_capabilities = pyqtSignal(str)
    configuration_loaded = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.url_label = QLabel("Please insert the base FHIR URL:")
        self.layout.addWidget(self.url_label)

        self.url_entry = QLineEdit()
        self.url_entry.setText("http://localhost:8080/fhir")
        self.layout.addWidget(self.url_entry)

        self.next_button = QPushButton("Show Resources")
        self.next_button.clicked.connect(self.submit_url)
        self.layout.addWidget(self.next_button)

        self.capabilities_button = QPushButton("Show Capabilities")
        self.capabilities_button.clicked.connect(self.display_capabilities)
        self.layout.addWidget(self.capabilities_button)

        self.load_configuration_button = QPushButton("Load Configuration")
        self.load_configuration_button.clicked.connect(self.load_configuration)
        self.layout.addWidget(self.load_configuration_button)

    def submit_url(self):
        url = self.url_entry.text()
        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a URL.")
        else:
            self.url_submitted.emit(url)

    def display_capabilities(self):
        url = self.url_entry.text()
        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a URL.")
        else:
            logger.debug(f"Displaying capabilities for {url}")
            self.show_capabilities.emit(url)

    def load_configuration(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Configuration File", "",
                                                   "JSON Files (*.json);;All Files (*)")
        if file_name:
            try:
                with open(file_name, 'r') as file:
                    config_data = json.load(file)
                self.configuration_loaded.emit(config_data)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load configuration file: {e}")