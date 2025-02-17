from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

class ResourceSummaryWidget(QWidget):
    back_requested = pyqtSignal()
    next_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.resource_counts_label = QLabel()
        self.layout.addWidget(self.resource_counts_label)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.request_next)
        self.layout.addWidget(self.next_button)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.request_back)
        self.layout.addWidget(self.back_button)

    def display_resource_counts(self, resource_counts):
        counts_text = "\n".join([f"{resource}: {count}" for resource, count in resource_counts.items()])
        self.resource_counts_label.setText(counts_text)

    def request_back(self):
        self.back_requested.emit()

    def request_next(self):
        self.next_requested.emit()
