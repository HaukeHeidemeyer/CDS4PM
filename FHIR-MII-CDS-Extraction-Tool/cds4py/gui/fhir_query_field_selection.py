from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem, QComboBox, QDateTimeEdit, \
    QLineEdit

from gui.main import logger


class FHIRQueryFieldSelectionWidget(QWidget):
    back_requested = pyqtSignal()
    query_created = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.parameters = {}

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.request_back)
        self.layout.addWidget(self.back_button)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Field", "Condition", "Value"])
        self.layout.addWidget(self.tree)

        self.SUPPORTED_RESOURCES = ["Encounter", "Condition", "Procedure", "Observation", "Patient"]

        self.create_query_button = QPushButton("Create Query")
        self.create_query_button.clicked.connect(self.create_query)
        self.layout.addWidget(self.create_query_button)

    def get_parameters(self, resource_name: str) -> dict:
        if resource_name.lower() == "encounter":
            return self.encounter_parameters
        elif resource_name.lower() == "condition":
            return self.condition_parameters
        elif resource_name.lower() == "procedure":
            return self.procedure_parameters
        elif resource_name.lower() == "observation":
            return self.observation_parameters
        elif resource_name.lower() == "patient":
            return self.patient_parameters
        else:
            return {}

    def populate_tree(self, resource_name: str) -> None:
        self.tree.clear()
        resource_dict = {
            "encounter": self.encounter_parameters,
            "condition": self.condition_parameters,
            "procedure": self.procedure_parameters,
            "observation": self.observation_parameters
        }

        parameters = resource_dict.get(resource_name.lower())
        if parameters:
            for key, value in parameters.items():
                item = QTreeWidgetItem([key])
                self.tree.addTopLevelItem(item)
                self.add_widgets_to_item(item, value)
        self.resource_name = resource_name

    def add_widgets_to_item(self, item: QTreeWidgetItem, value_type: str) -> None:
        print(value_type)
        combo = QComboBox()
        if value_type == "date":
            combo.addItems(["None", "ge", "le", "sa", "eb", "ap"])
        elif value_type == "quantity":
            combo.addItems(["None", "ge", "le", "lt", "gt", "eq", "ne"])
        elif value_type == "token":
            combo.addItems(["None", "eq", "ne", "in", "not in", "contains", "exact"])
        else:
            combo.addItems(["None", "eq", "ne"])
        combo.currentIndexChanged.connect(lambda idx, itm=item: self.condition_changed(idx, itm))
        self.tree.setItemWidget(item, 1, combo)

        if value_type == "date":
            date_edit = QDateTimeEdit()
            date_edit.setCalendarPopup(True)
            self.tree.setItemWidget(item, 2, date_edit)
        elif value_type == "quantity":
            quantity_edit = QLineEdit()
            quantity_edit.setValidator(QDoubleValidator())
            self.tree.setItemWidget(item, 2, quantity_edit)
        else:
            line_edit = QLineEdit()
            self.tree.setItemWidget(item, 2, line_edit)

    def condition_changed(self, index: int, item: QTreeWidgetItem) -> None:
        if index != 0:  # Not "None"
            self.duplicate_item(item)
        else:
            self.remove_duplicates(item)

    def duplicate_item(self, item: QTreeWidgetItem) -> None:
        # Check if an item with the same field and condition "None" already exists
        for i in range(self.tree.topLevelItemCount()):
            existing_item = self.tree.topLevelItem(i)
            if existing_item.text(0) == item.text(0):
                condition_widget = self.tree.itemWidget(existing_item, 1)
                if condition_widget and condition_widget.currentText() == "None":
                    return

        self.parameters = self.get_parameters(self.resource_name)

        # Insert a new item with the same field
        new_item = QTreeWidgetItem([item.text(0)])
        self.tree.insertTopLevelItem(self.tree.indexOfTopLevelItem(item) + 1, new_item)
        self.add_widgets_to_item(new_item, self.parameters[item.text(0)])



    def remove_duplicates(self, item: QTreeWidgetItem) -> None:
        index = self.tree.indexOfTopLevelItem(item)
        while index + 1 < self.tree.topLevelItemCount() and self.tree.topLevelItem(index + 1).text(0) == item.text(0):
            self.tree.takeTopLevelItem(index + 1)

    def create_query(self) -> None:
        query_parts = []
        root = self.tree.invisibleRootItem()
        self.traverse_tree(root, query_parts, "")
        query = "&".join(query_parts)
        full_query = f"{self.base_url}/{self.resource_name}?{query}"
        logger.info(f"Query created: {full_query}")
        self.query_created.emit(full_query)

    def traverse_tree(self, item: QTreeWidgetItem, query_parts: list, prefix: str) -> None:
        for i in range(item.childCount()):
            child = item.child(i)
            field = child.text(0)
            condition_widget = self.tree.itemWidget(child, 1)
            value_widget = self.tree.itemWidget(child, 2)
            if isinstance(condition_widget, QComboBox) and condition_widget.currentText() != "None":
                condition = condition_widget.currentText()
                if isinstance(value_widget, QDateTimeEdit):
                    value = value_widget.dateTime().toString(format=Qt.DateFormat.ISODate)
                elif isinstance(value_widget, QLineEdit):
                    value = value_widget.text()
                else:
                    continue
                if value != "":
                    query_parts.append(f"{field}={condition}{value}")
            self.traverse_tree(child, query_parts, prefix)

    def request_back(self) -> None:
        self.back_requested.emit()
