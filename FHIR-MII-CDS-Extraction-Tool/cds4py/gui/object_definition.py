import os
import importlib.util
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit,
    QComboBox, QCheckBox, QGridLayout, QListWidget, QListWidgetItem, QMessageBox,
    QScrollArea
)
from PyQt6.QtCore import pyqtSignal, Qt
import logging

from cds4py.utils.plugins import load_plugins, load_modifiers

logger = logging.getLogger(__name__)

class DefineObjectTypesWidget(QWidget):
    back_requested = pyqtSignal()
    next_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.resource_tables = None
        self.layout = QVBoxLayout(self)

        self.label = QLabel("Define Object Types")
        self.label.setStyleSheet("font-weight: bold; font-size: 30px;")
        self.layout.addWidget(self.label)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.request_back)
        self.layout.addWidget(self.back_button)

        self.object_list = QListWidget()
        self.object_list.itemClicked.connect(self.edit_object_definition)
        self.layout.addWidget(self.object_list)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.object_definitions_layout = QGridLayout()
        self.scroll_layout.addLayout(self.object_definitions_layout)
        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area)

        self.add_object_button = QPushButton("Add Object")
        self.add_object_button.clicked.connect(self.save_current_object_and_add_new)
        self.layout.addWidget(self.add_object_button)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.request_next)
        self.layout.addWidget(self.next_button)

        self.current_resource = None
        self.object_definitions = {}
        self.current_definition = None
        self.plugins = load_plugins()
        self.modifiers = load_modifiers()
        self.current_resource_index = 0
        self.object_names = []

    def set_resource_tables(self, resource_tables):
        self.resource_tables = resource_tables

    def update_selected_resources(self, selected_resources):
        self.selected_resources = selected_resources
        self.resource_list = selected_resources
        self.current_resource_index = 0
        self.display_object_definitions()

    def display_object_definitions(self):
        if not self.selected_resources:
            return

        self.current_resource = self.selected_resources[self.current_resource_index]
        self.label.setText(f"Define Object Types - {self.current_resource}")
        self.clear_object_definitions()

        self.object_list.clear()
        if self.current_resource in self.object_definitions:
            for obj_name in self.object_definitions[self.current_resource]:
                self.object_list.addItem(obj_name)

        self.create_initial_object_definition()  # Ensure an empty definition is always displayed

    def save_current_object_and_add_new(self):
        self.save_current_object()
        self.create_initial_object_definition()

    def save_current_object(self, check_name=True):

        object_name = self.current_definition["name"].text()
        if object_name == "":
            # Nothing to save
            return
        if check_name:
            if not object_name or object_name == "" or object_name.isspace():
                QMessageBox.warning(self, "Warning", "Please provide a name for the object.")
                return
            if object_name in self.object_names:
                QMessageBox.warning(self, "Warning", "An object with this name already exists.")
                return

        if self.current_resource not in self.object_definitions:
            self.object_definitions[self.current_resource] = {}

        self.object_definitions[self.current_resource][object_name] = self.get_definition_values()
        if not self.object_list.findItems(object_name, Qt.MatchFlag.MatchExactly):
            self.object_list.addItem(object_name)

        logger.debug(f"Object {object_name} saved for resource {self.current_resource}")

    def create_initial_object_definition(self):
        self.current_definition = self.create_empty_definition()
        self.add_definition_to_layout(self.current_definition)

    def create_empty_definition(self):
        definition = {
            "name": QLineEdit(),
            "attributes": []
        }
        columns = self.resource_tables[self.current_resource].columns.tolist()
        for column_name in columns:
            attribute = {
                "column_name": QLabel(column_name),
                "include": QCheckBox("Include"),
                "modifier": QComboBox(),
                "modifier_param": QLineEdit(),
                "condition": QComboBox(),
                "value": QLineEdit()
            }
            attribute["modifier"].addItems(["None"])  # Add default modifier
            for modifier in self.modifiers:
                # TODO: Check if modifier is applicable to the current resource
                # if modifier.is_applicable_to(self.current_resource):
                attribute["modifier"].addItem(modifier.name)
            attribute["condition"].addItems(["None"])  # Add default condition
            for plugin in self.plugins:
                # TODO: Check if plugin is applicable to the current resource
                # if plugin.is_applicable_to(self.current_resource):
                attribute["condition"].addItem(plugin.name)
            unique_values = self.get_unique_values(column_name, 5)
            attribute["value"].setPlaceholderText(", ".join(unique_values))
            definition["attributes"].append(attribute)
        return definition

    def get_unique_values(self, column_name, limit):
        unique_values = self.resource_tables[self.current_resource][column_name].dropna().unique().tolist()
        return [str(value) for value in unique_values[:limit]]

    def get_definition_values(self):
        definition = {
            "name": self.current_definition["name"].text(),
            "attributes": []
        }
        for attribute in self.current_definition["attributes"]:
            attr_values = {
                "column_name": attribute["column_name"].text(),
                "include": attribute["include"].isChecked(),
                "modifier": attribute["modifier"].currentText(),
                "modifier_param": attribute["modifier_param"].text(),
                "condition": attribute["condition"].currentText(),
                "value": attribute["value"].text() if attribute["value"].text() else ""
            }
            definition["attributes"].append(attr_values)
        return definition

    def add_definition_to_layout(self, definition, row=0):
        self.clear_object_definitions()  # Clear previous definitions before adding new
        self.object_definitions_layout.addWidget(QLabel("Object Type Name"), row, 0)
        self.object_definitions_layout.addWidget(definition["name"], row, 1)
        for i, attribute in enumerate(definition["attributes"]):
            self.object_definitions_layout.addWidget(attribute["column_name"], row + i + 1, 0)
            self.object_definitions_layout.addWidget(attribute["include"], row + i + 1, 1)
            self.object_definitions_layout.addWidget(attribute["modifier"], row + i + 1, 2)
            self.object_definitions_layout.addWidget(attribute["modifier_param"], row + i + 1, 3)
            self.object_definitions_layout.addWidget(attribute["condition"], row + i + 1, 4)
            self.object_definitions_layout.addWidget(attribute["value"], row + i + 1, 5)

    def clear_object_definitions(self):
        while self.object_definitions_layout.count():
            item = self.object_definitions_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def edit_object_definition(self, item):
        object_name = item.text()
        if self.current_resource in self.object_definitions:
            definition_values = self.object_definitions[self.current_resource][object_name]
            self.current_definition = self.create_empty_definition()
            self.current_definition["name"].setText(definition_values["name"])
            for attribute, values in zip(self.current_definition["attributes"], definition_values["attributes"]):
                attribute["include"].setChecked(values["include"])
                attribute["modifier"].setCurrentText(values["modifier"])
                attribute["modifier_param"].setText(values["modifier_param"])
                attribute["condition"].setCurrentText(values["condition"])
                attribute["value"].setText(values["value"])
            self.add_definition_to_layout(self.current_definition)

    def request_back(self):
        self.back_requested.emit()

    def request_next(self):
        self.save_current_object(check_name=False)
        if not self.object_definitions or all(len(v) == 0 for v in self.object_definitions.values()):
            QMessageBox.warning(self, "Warning", "Please define at least one object before proceeding.")
            return
        if self.current_resource_index < len(self.selected_resources) - 1:
            self.current_resource_index += 1
            self.display_object_definitions()
        else:
            self.next_requested.emit()

    def get_all_object_definitions(self):
        logger.debug(f"Collected Object Definitions: {self.object_definitions}")
        return self.object_definitions
