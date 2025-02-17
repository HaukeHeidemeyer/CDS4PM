from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QPushButton, QMessageBox
from PyQt6.QtCore import pyqtSignal

class SelectResourceTypesWidget(QWidget):
    next_requested = pyqtSignal(list)
    back_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.label = QLabel("Please select the resource types used for OCEL Object generation:")
        self.label.setStyleSheet("font-weight: bold; font-size: 30px;")
        self.layout.addWidget(self.label)

        self.checkboxes = {}
        self.checkbox_layout = QVBoxLayout()
        self.layout.addLayout(self.checkbox_layout)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.validate_selection)
        self.layout.addWidget(self.next_button)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.request_back)
        self.layout.addWidget(self.back_button)

    def populate_checkboxes(self, resource_counts, existing_selections=None):
        # Clear existing checkboxes
        for i in reversed(range(self.checkbox_layout.count())):
            widget_to_remove = self.checkbox_layout.itemAt(i).widget()
            if widget_to_remove:
                widget_to_remove.setParent(None)

        # Create checkboxes for each resource type
        for resource_type in resource_counts.keys():
            checkbox = QCheckBox(resource_type)
            self.checkboxes[resource_type] = checkbox
            self.checkbox_layout.addWidget(checkbox)
            if existing_selections and resource_type in existing_selections:
                checkbox.setChecked(True)

    def validate_selection(self):
        selected_resources = [resource for resource, checkbox in self.checkboxes.items() if checkbox.isChecked()]
        if not selected_resources:
            QMessageBox.warning(self, "Warning", "Please select at least one resource type.")
        else:
            self.next_requested.emit(selected_resources)

    def request_back(self):
        self.back_requested.emit()
