from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QCheckBox, QGridLayout
from PyQt6.QtCore import pyqtSignal

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QCheckBox, QGridLayout
from PyQt6.QtCore import pyqtSignal

class SelectEventResourcesWidget(QWidget):
    back_requested = pyqtSignal()
    next_requested = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.label = QLabel("Select FHIR Resources for Event Creation")
        self.label.setStyleSheet("font-weight: bold; font-size: 30px;")
        self.layout.addWidget(self.label)

        self.resource_layout = QGridLayout()
        self.layout.addLayout(self.resource_layout)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.request_back)
        self.layout.addWidget(self.back_button)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.request_next)
        self.layout.addWidget(self.next_button)

        self.resource_checkboxes = []

    def populate_checkboxes(self, resource_counts, selected_resources=None):
        self.clear_layout()
        self.resource_checkboxes = []
        for i, (resource_type, count) in enumerate(resource_counts.items()):
            checkbox = QCheckBox(f"{resource_type} ({count})")
            if selected_resources and resource_type in selected_resources:
                checkbox.setChecked(True)
            self.resource_layout.addWidget(checkbox, i // 3, i % 3)
            self.resource_checkboxes.append(checkbox)

    def clear_layout(self):
        while self.resource_layout.count():
            item = self.resource_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def request_back(self):
        self.back_requested.emit()

    def request_next(self):
        selected_resources = [checkbox.text().split(" ")[0] for checkbox in self.resource_checkboxes if checkbox.isChecked()]
        self.next_requested.emit(selected_resources)
