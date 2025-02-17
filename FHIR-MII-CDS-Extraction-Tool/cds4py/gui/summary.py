

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea
)
from PyQt6.QtCore import pyqtSignal
import json

from cds4py.gui.utils.datamanager import DataManager


class SummaryWidget(QWidget):
    back_requested = pyqtSignal()
    start_extraction_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.label = QLabel("Summary")
        self.label.setStyleSheet("font-weight: bold; font-size: 30px;")
        self.layout.addWidget(self.label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area)

        self.summary_label = QLabel()
        self.scroll_layout.addWidget(self.summary_label)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.request_back)
        self.layout.addWidget(self.back_button)

        self.start_button = QPushButton("Start Extraction")
        self.start_button.clicked.connect(self.start_extraction)
        self.layout.addWidget(self.start_button)

    def set_data(self, dm: DataManager):
        #summary_text = "Selected Resources:\n" + "\n".join(dm.selected_resources) + "\n\n"
        summary_text = "Defined Objects:\n" + json.dumps(dm.defined_objects, indent=2) + "\n\n"
        summary_text += "FHIR Query:\n" + dm.fhir_query + "\n\n"
        summary_text += "Defined Object Relations:\n" + json.dumps(dm.object_relations, indent=2) + "\n\n"
        summary_text += "Defined Events:\n" + json.dumps(dm.defined_events, indent=2)
        self.summary_label.setText(summary_text)

    def request_back(self):
        self.back_requested.emit()

    def start_extraction(self):
        self.start_extraction_requested.emit()
