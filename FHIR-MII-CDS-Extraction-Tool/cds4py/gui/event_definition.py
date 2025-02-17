import os
import importlib.util
import re
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox, QCheckBox, QGridLayout, QListWidget, QMessageBox, QScrollArea
)
from PyQt6.QtCore import pyqtSignal, Qt
import logging

from plugins.basecondition import BaseCondition
from plugins.basemodifier import BaseModifier
from utils.plugins import load_plugins, load_modifiers

logger = logging.getLogger(__name__)

class EventDefinitionWidget(QWidget):
    back_requested = pyqtSignal()
    next_requested = pyqtSignal()
    event_defined = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.label = QLabel("Define Events")
        self.label.setStyleSheet("font-weight: bold; font-size: 30px;")
        self.layout.addWidget(self.label)

        self.event_list = QListWidget()
        self.event_list.itemClicked.connect(self.edit_event_definition)
        self.layout.addWidget(self.event_list)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.event_definitions_layout = QGridLayout()
        self.scroll_layout.addLayout(self.event_definitions_layout)
        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area)

        self.add_event_button = QPushButton("Add Event")
        self.add_event_button.clicked.connect(self.save_current_event_and_add_new)
        self.layout.addWidget(self.add_event_button)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.request_next)
        self.layout.addWidget(self.next_button)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.request_back)
        self.layout.addWidget(self.back_button)

        self.object_definitions = {}
        self.relations = None
        self.selected_event_resources = None
        self.query_data = None

        self.current_event_definition = None
        self.event_definitions = {}

        self.current_resource_index = 0

        self.plugins = load_plugins()
        self.modifiers = load_modifiers()

    def set_data(self, selected_event_resources, query_data, object_definitions):
        self.selected_event_resources = selected_event_resources
        self.query_data = query_data
        self.object_definitions = object_definitions
        self.display_event_definitions()

    def display_event_definitions(self):
        if not self.selected_event_resources:
            return

        self.clear_layout()
        self.event_list.clear()

        resource_type = self.selected_event_resources[self.current_resource_index]
        self.label.setText(f"Define Events - {resource_type}")

        if resource_type in self.event_definitions:
            for event_name in self.event_definitions[resource_type]:
                self.event_list.addItem(event_name)

        self.create_initial_event_definition()

    def clear_layout(self):
        while self.event_definitions_layout.count():
            item = self.event_definitions_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def create_initial_event_definition(self):
        self.current_event_definition = self.create_empty_definition()
        self.add_definition_to_layout(self.current_event_definition)

    def create_empty_definition(self):
        definition = {
            "event_name": QLineEdit(),
            "timestamp": QComboBox(),
            "attributes": []
        }
        columns = self.get_all_columns()
        datetime_columns = self.get_datetime_columns()

        for column_name in columns:
            attribute = {
                "column_name": QLabel(column_name),
                "include": QCheckBox("Include"),
                "condition": QComboBox(),
                "condition_value": QLineEdit(),
                "modifier": QComboBox(),
                "modifier_value": QLineEdit(),
                "add_to_event_name": QCheckBox("Add to event type name")
            }
            attribute["condition"].addItems(["None"])  # Add default condition
            for plugin in self.plugins:
                attribute["condition"].addItem(plugin.name)
            attribute["modifier"].addItems(["None"])  # Add default modifier
            for modifier in self.modifiers:
                attribute["modifier"].addItem(modifier.name)
            definition["attributes"].append(attribute)

        definition["timestamp"].addItems(datetime_columns)

        return definition

    def get_all_columns(self):
        resource_type = self.selected_event_resources[self.current_resource_index]
        return self.query_data[resource_type].columns.tolist()

    def get_datetime_columns(self):
        resource_type = self.selected_event_resources[self.current_resource_index]
        date_pattern = re.compile(r'([0-9]{4})-([0-1][0-9])-([0-3][0-9])')
        time_pattern = re.compile(r'([0-2][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?')
        datetime_pattern = re.compile(r'([0-9]{4})-([0-1][0-9])-([0-3][0-9])T([0-2][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|(\+|-)((0[0-9]|1[0-3]):[0-5][0-9]|14:00))')
        datetime_columns = set()
        df = self.query_data[resource_type]
        for column in df.columns:
            if df[column].dropna().astype(str).apply(lambda x: bool(date_pattern.match(x)) or bool(time_pattern.match(x)) or bool(datetime_pattern.match(x))).any():
                datetime_columns.add(column)
        return list(datetime_columns)

    def add_definition_to_layout(self, definition, row=0):
        self.clear_layout()

        self.event_definitions_layout.addWidget(QLabel("Event Type Name"), row, 0)
        self.event_definitions_layout.addWidget(definition["event_name"], row, 1)
        row += 1

        self.event_definitions_layout.addWidget(QLabel("Timestamp"), row, 0)
        self.event_definitions_layout.addWidget(definition["timestamp"], row, 1)
        row += 1

        for i, attribute in enumerate(definition["attributes"]):
            self.event_definitions_layout.addWidget(attribute["column_name"], row + i, 0)
            self.event_definitions_layout.addWidget(attribute["include"], row + i, 1)
            self.event_definitions_layout.addWidget(attribute["condition"], row + i, 2)
            self.event_definitions_layout.addWidget(attribute["condition_value"], row + i, 3)
            self.event_definitions_layout.addWidget(attribute["modifier"], row + i, 4)
            self.event_definitions_layout.addWidget(attribute["modifier_value"], row + i, 5)
            self.event_definitions_layout.addWidget(attribute["add_to_event_name"], row + i, 6)

        row += len(definition["attributes"])

        # Add Event Object Relations section
        self.event_definitions_layout.addWidget(QLabel("Event Object Relations"), row, 0, 1, 7, alignment=Qt.AlignmentFlag.AlignCenter)
        self.event_definitions_layout.itemAtPosition(row, 0).widget().setStyleSheet("font-weight: bold; font-size: 20px;")
        row += 1

        resource_type = self.selected_event_resources[self.current_resource_index]
        reference_columns = [col for col in self.query_data[resource_type].columns if col.endswith('_reference')]
        for column_name in reference_columns:
            self.add_relation_row(resource_type, column_name, row)
            row += 1

        # Add relations to objects created from the same resource type
        self.add_same_resource_relations(resource_type, row)

    def add_relation_row(self, resource_type, column_name, row=None):
        if row is None:
            row = self.event_definitions_layout.rowCount()

        # Create the widgets
        label = QLabel(column_name)
        condition_label = QLabel("Condition")
        condition_combo = QComboBox()
        condition_combo.addItems(["None"] + [plugin.name for plugin in self.plugins])

        condition_param_label = QLabel("Condition Param")
        condition_param_text = QLineEdit()

        qualifier_label = QLabel("Qualifier")
        qualifier_text = QLineEdit()

        target_field_label = QLabel("Target Field")
        target_field_combo = QComboBox()
        target_field_combo.addItems(
            [col for col in self.query_data[resource_type].columns if col.endswith('_reference')])

        related_object_label = QLabel("Related Object")
        related_object_combo = QComboBox()
        all_defined_objects = [f"{res}: {obj}" for res, objs in self.object_definitions.items() for obj in objs.keys()]
        related_object_combo.addItems(all_defined_objects)

        add_button = QPushButton("+")
        add_button.clicked.connect(lambda: self.add_relation_row(resource_type, column_name))

        # Add widgets to layout
        self.event_definitions_layout.addWidget(label, row, 0)
        self.event_definitions_layout.addWidget(condition_label, row, 1)
        self.event_definitions_layout.addWidget(condition_combo, row, 2)
        self.event_definitions_layout.addWidget(condition_param_label, row, 3)
        self.event_definitions_layout.addWidget(condition_param_text, row, 4)
        self.event_definitions_layout.addWidget(qualifier_label, row, 5)
        self.event_definitions_layout.addWidget(qualifier_text, row, 6)
        self.event_definitions_layout.addWidget(target_field_label, row, 7)
        self.event_definitions_layout.addWidget(target_field_combo, row, 8)
        self.event_definitions_layout.addWidget(related_object_label, row, 9)
        self.event_definitions_layout.addWidget(related_object_combo, row, 10)
        self.event_definitions_layout.addWidget(add_button, row, 11)

        # Store the references to widgets in current_event_definition
        if "relation_widgets" not in self.current_event_definition:
            self.current_event_definition["relation_widgets"] = []

        self.current_event_definition["relation_widgets"].append({
            "column_name": column_name,
            "condition_combo": condition_combo,
            "condition_param_text": condition_param_text,
            "qualifier_text": qualifier_text,
            "target_field_combo": target_field_combo,
            "related_object_combo": related_object_combo,
        })

    def add_same_resource_relations(self, resource_type, row):
        for object_name in self.object_definitions.get(resource_type, {}):
            label = QLabel(f"Related to {object_name}")
            qualifier_text = QLineEdit()
            self.event_definitions_layout.addWidget(label, row, 0)
            self.event_definitions_layout.addWidget(qualifier_text, row, 1)
            row += 1

    def save_current_event_and_add_new(self):
        self.save_current_event()
        self.create_initial_event_definition()

    def save_current_event(self, warning=True):
        if self.current_event_definition is None:
            return

        event_name = self.current_event_definition["event_name"].text()
        if not event_name and warning:
            QMessageBox.warning(self, "Warning", "Please provide a name for the event.")
            return

        timestamp = self.current_event_definition["timestamp"].currentText()

        if not self.selected_event_resources:
            return

        resource_type = self.selected_event_resources[self.current_resource_index]
        if resource_type not in self.event_definitions:
            self.event_definitions[resource_type] = {}

        self.event_definitions[resource_type][event_name] = self.get_definition_values()
        if not self.event_list.findItems(event_name, Qt.MatchFlag.MatchExactly):
            self.event_list.addItem(event_name)

    def get_definition_values(self):
        definition = {
            "event_name": self.current_event_definition["event_name"].text(),
            "timestamp": self.current_event_definition["timestamp"].currentText(),
            "attributes": [],
            "relations": []
        }

        for attribute in self.current_event_definition["attributes"]:
            attr_values = {
                "column_name": attribute["column_name"].text(),
                "include": attribute["include"].isChecked(),
                "condition": attribute["condition"].currentText(),
                "condition_value": attribute["condition_value"].text(),
                "modifier": attribute["modifier"].currentText(),
                "modifier_value": attribute["modifier_value"].text(),
                "add_to_event_name": attribute["add_to_event_name"].isChecked()
            }
            definition["attributes"].append(attr_values)

        resource_type = self.selected_event_resources[self.current_resource_index]

        # Handle same resource relations
        for i in range(self.event_definitions_layout.rowCount()):
            item = self.event_definitions_layout.itemAtPosition(i, 0)
            if item and isinstance(item.widget(), QLabel) and item.widget().text().startswith('Related to'):
                qualifier_widget = self.event_definitions_layout.itemAtPosition(i, 1).widget()
                qualifier = qualifier_widget.text() if qualifier_widget and isinstance(qualifier_widget, QLineEdit) else ""
                if qualifier:
                    object_name = item.widget().text().replace('Related to ', '')
                    definition["relations"].append({
                        "resource_type": resource_type,
                        "object_name": object_name,
                        "qualifier": qualifier,
                        "related_object": f"{resource_type}: {object_name}"
                    })

        # Handle other relations
        for i in range(self.event_definitions_layout.rowCount()):
            item = self.event_definitions_layout.itemAtPosition(i, 0)
            if item and isinstance(item.widget(), QLabel) and item.widget().text().endswith('_reference'):
                condition_combo = self.event_definitions_layout.itemAtPosition(i, 2)
                condition = condition_combo.widget().currentText() if condition_combo and isinstance(condition_combo.widget(), QComboBox) else ""

                condition_param_widget = self.event_definitions_layout.itemAtPosition(i, 4)
                condition_param = condition_param_widget.widget().text() if condition_param_widget and isinstance(condition_param_widget.widget(), QLineEdit) else ""

                qualifier_widget = self.event_definitions_layout.itemAtPosition(i, 6)
                qualifier = qualifier_widget.widget().text() if qualifier_widget and isinstance(qualifier_widget.widget(), QLineEdit) else ""

                target_field_widget = self.event_definitions_layout.itemAtPosition(i, 8)
                target_field = target_field_widget.widget().currentText() if target_field_widget and isinstance(target_field_widget.widget(), QComboBox) else ""

                related_object_widget = self.event_definitions_layout.itemAtPosition(i, 10)
                related_object = related_object_widget.widget().currentText() if related_object_widget and isinstance(related_object_widget.widget(), QComboBox) else ""

                if qualifier:  # Only store if qualifier is not empty
                    definition["relations"].append({
                        "reference": item.widget().text(),
                        "condition": condition,
                        "condition_param": condition_param,
                        "qualifier": qualifier,
                        "target_field": target_field,
                        "related_object": related_object,
                        "resource_type": resource_type
                    })

        return definition

    def edit_event_definition(self, item):
        event_name = item.text()
        resource_type = self.selected_event_resources[self.current_resource_index]

        if resource_type in self.event_definitions:
            definition_values = self.event_definitions[resource_type][event_name]
            self.current_event_definition = self.create_empty_definition()
            self.current_event_definition["event_name"].setText(definition_values["event_name"])
            self.current_event_definition["timestamp"].setCurrentText(definition_values["timestamp"])

            # Set attributes
            for attribute, values in zip(self.current_event_definition["attributes"], definition_values["attributes"]):
                attribute["include"].setChecked(values["include"])
                attribute["condition"].setCurrentText(values["condition"])
                attribute["condition_value"].setText(values["condition_value"])
                attribute["modifier"].setCurrentText(values["modifier"])
                attribute["modifier_value"].setText(values["modifier_value"])
                attribute["add_to_event_name"].setChecked(values["add_to_event_name"])

            # Recreate the layout to show the current event definition
            self.add_definition_to_layout(self.current_event_definition)

            # Set relations
            for relation, widgets in zip(definition_values.get("relations", []),
                                         self.current_event_definition.get("relation_widgets", [])):
                if "reference" in relation:
                    widgets["condition_combo"].setCurrentText(relation["condition"])
                    widgets["condition_param_text"].setText(relation["condition_param"])
                    widgets["qualifier_text"].setText(relation["qualifier"])
                    widgets["target_field_combo"].setCurrentText(relation["target_field"])
                    widgets["related_object_combo"].setCurrentText(relation["related_object"])
                if 'object_name' in relation:
                    for i in range(self.event_definitions_layout.rowCount()):
                        item = self.event_definitions_layout.itemAtPosition(i, 0)
                        if item and isinstance(item.widget(),
                                               QLabel) and item.widget().text() == f"Related to {relation['object_name']}":
                            qualifier_widget = self.event_definitions_layout.itemAtPosition(i, 1).widget()
                            if isinstance(qualifier_widget, QLineEdit):
                                qualifier_widget.setText(relation["qualifier"])

    def define_event(self):
        self.save_current_event()
        self.event_defined.emit(self.event_definitions)

    def request_next(self):
        self.save_current_event(warning=False)
        if self.current_resource_index < len(self.selected_event_resources) - 1:
            self.current_resource_index += 1
            self.display_event_definitions()
        else:
            self.event_defined.emit(self.event_definitions)

    def request_back(self):
        if self.current_resource_index > 0:
            self.current_resource_index -= 1
            self.display_event_definitions()
        else:
            self.back_requested.emit()