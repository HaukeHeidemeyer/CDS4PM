import os
import importlib.util
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit,
    QComboBox, QGridLayout, QMessageBox, QScrollArea
)
from PyQt6.QtCore import pyqtSignal, Qt
import logging

logger = logging.getLogger(__name__)

class ObjectRelationWidget(QWidget):
    relations_defined = pyqtSignal(dict)
    next_requested = pyqtSignal()
    back_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.label = QLabel("Define Object Relations")
        self.label.setStyleSheet("font-weight: bold; font-size: 30px;")
        self.layout.addWidget(self.label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.object_relations_layout = QGridLayout()
        self.scroll_layout.addLayout(self.object_relations_layout)
        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.request_back)
        self.layout.addWidget(self.back_button)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.request_next)
        self.layout.addWidget(self.next_button)

        # Instance variables to store data
        self.object_definitions = None
        self.plugins = None
        self.resource_tables = None

        self.row_count = 0  # Track the number of rows

    def set_data(self, object_definitions, plugins, resource_tables):
        self.object_definitions = object_definitions
        self.plugins = plugins
        self.resource_tables = resource_tables
        self.display_object_relations()

    def display_object_relations(self):
        self.row_count = 0
        self.clear_layout()

        for resource_type, definitions in self.object_definitions.items():
            for object_type in definitions.keys():
                self.add_relation_row(resource_type, object_type)

    def clear_layout(self):
        while self.object_relations_layout.count():
            item = self.object_relations_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def add_relation_row(self, resource_type, object_type, relation=None):
        row = self.row_count

        label = QLabel(f"{resource_type}: {object_type}")
        self.object_relations_layout.addWidget(label, row, 0)

        condition_combo = QComboBox()
        condition_combo.addItems(["None"] + [plugin.name for plugin in self.plugins])
        if relation:
            condition_combo.setCurrentText(relation["condition"])
        self.object_relations_layout.addWidget(QLabel("Condition"), row, 1)
        self.object_relations_layout.addWidget(condition_combo, row, 2)

        condition_param_text = QLineEdit()
        if relation:
            condition_param_text.setText(relation["condition_param"])
        self.object_relations_layout.addWidget(QLabel("Condition Param"), row, 3)
        self.object_relations_layout.addWidget(condition_param_text, row, 4)

        qualifier_text = QLineEdit()
        if relation:
            qualifier_text.setText(relation["qualifier"])
        self.object_relations_layout.addWidget(QLabel("Qualifier"), row, 5)
        self.object_relations_layout.addWidget(qualifier_text, row, 6)

        target_field_combo = QComboBox()
        target_field_combo.addItems(self.resource_tables[resource_type].columns.tolist())
        if relation:
            target_field_combo.setCurrentText(relation["target_field"])
        self.object_relations_layout.addWidget(QLabel("Target Field"), row, 7)
        self.object_relations_layout.addWidget(target_field_combo, row, 8)

        reference_combo = QComboBox()
        reference_columns = [col for col in self.resource_tables[resource_type].columns if col.endswith('_reference')]
        reference_combo.addItems(reference_columns)
        if relation:
            reference_combo.setCurrentText(relation["reference"])
        self.object_relations_layout.addWidget(QLabel("Reference"), row, 9)
        self.object_relations_layout.addWidget(reference_combo, row, 10)

        related_object_combo = QComboBox()
        all_defined_objects = [f"{res}: {obj}" for res, objs in self.object_definitions.items() for obj in objs.keys()]
        related_object_combo.addItems(all_defined_objects)
        if relation:
            related_object_combo.setCurrentText(relation["related_object"])
        self.object_relations_layout.addWidget(QLabel("Related Object"), row, 11)
        self.object_relations_layout.addWidget(related_object_combo, row, 12)

        add_button = QPushButton("+")
        add_button.clicked.connect(lambda: self.add_relation_row(resource_type, object_type))
        self.object_relations_layout.addWidget(add_button, row, 13)

        self.row_count += 1

    def define_relations(self):
        """
        Collect and emit the defined relations.
        """
        object_relations = {}
        for row in range(self.row_count):
            if self.object_relations_layout.itemAtPosition(row, 0) is None:
                continue

            resource_and_object = self.object_relations_layout.itemAtPosition(row, 0).widget().text()
            resource_type, object_type = resource_and_object.split(": ", 1)

            condition = self.object_relations_layout.itemAtPosition(row, 2).widget().currentText()
            condition_param = self.object_relations_layout.itemAtPosition(row, 4).widget().text()
            qualifier = self.object_relations_layout.itemAtPosition(row, 6).widget().text()
            target_field = self.object_relations_layout.itemAtPosition(row, 8).widget().currentText()
            reference = self.object_relations_layout.itemAtPosition(row, 10).widget().currentText()
            related_object = self.object_relations_layout.itemAtPosition(row, 12).widget().currentText()

            if qualifier:  # Only store if qualifier is not empty
                if resource_type not in object_relations:
                    object_relations[resource_type] = []

                object_relations[resource_type].append({
                    "source_object": object_type,
                    "condition": condition,
                    "condition_param": condition_param,
                    "qualifier": qualifier,
                    "target_field": target_field,
                    "reference": reference,
                    "related_object": related_object
                })

        self.relations_defined.emit(object_relations)  # Emit updated relations

    def request_next(self):
        """
        Handle the next button click.
        """
        self.define_relations()
        self.next_requested.emit()

    def request_back(self):
        """
        Handle the back button click.
        """
        self.back_requested.emit()
