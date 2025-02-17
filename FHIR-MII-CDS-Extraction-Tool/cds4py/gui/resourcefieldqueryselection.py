from abc import ABC, abstractmethod
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QComboBox, QDateTimeEdit, QLineEdit, QPushButton, QMessageBox, QLabel, QCheckBox
)
from PyQt6.QtGui import QDoubleValidator, QFont

class MetaWidget(type(QWidget), type(ABC)):
    # This metaclass is used to ensure that the class is a subclass of QWidget and ABC
    pass

class ResourceFieldQuerySelection(QWidget, ABC, metaclass=MetaWidget):
    back_requested = pyqtSignal()
    next_requested = pyqtSignal()

    def __init__(self, resource_name: str):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.request_back)
        self.layout.addWidget(self.back_button)

        self.title_label = QLabel(resource_name)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(30)
        self.title_label.setFont(font)
        self.layout.addWidget(self.title_label)

        self.include_resource: bool = False

        if resource_name != "Encounter":
            self.include_resource_cb = QCheckBox("Include resource")
            self.layout.addWidget(self.include_resource_cb)
            self.include_resource_cb.clicked.connect(self.include_resource_checkbox_clicked)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Field", "Condition", "Value"])
        self.layout.addWidget(self.tree)

        self.next_button = QPushButton("Next")
        # self.next_button.clicked.connect(self.next)
        self.next_button.clicked.connect(self.request_next)
        self.layout.addWidget(self.next_button)

        self.parameters = self.get_parameters()
        self.populate_tree()
        self.show()

    @abstractmethod
    def get_parameters(self):
        pass

    def populate_tree(self):
        self.tree.clear()
        parameters = self.get_parameters()
        for key, value in parameters.items():
            if value != "reference":
                item = QTreeWidgetItem([key])
                self.tree.addTopLevelItem(item)
                self.add_widgets_to_item(item, value)

    def add_widgets_to_item(self, item: QTreeWidgetItem, value_type: str) -> None:
        combo = QComboBox()
        if value_type == "date" or value_type == "quantity":
            combo.addItems(["None", "=", ">", "<", ">=", "<=", "!=", "sa", "eb", "ap"])
        elif value_type == "token":
            combo.addItems(["None", "=", "text", "not", "above", "below", "in", "not-in", "of-type", "contains", "exact"])
        elif value_type == "string":
            combo.addItems(["None", "=", "contains", "exact"])
        elif value_type == "uri":
            combo.addItems(["None", "=", "below", "above"])
        elif value_type == "token":
            combo.addItems(["None", "="])
        else:
            combo.addItems(["None", "=", "eq", "ne"])
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

        # Insert a new item with the same field
        new_item = QTreeWidgetItem([item.text(0)])
        self.tree.insertTopLevelItem(self.tree.indexOfTopLevelItem(item) + 1, new_item)
        self.add_widgets_to_item(new_item, self.parameters[item.text(0)])

    def remove_duplicates(self, item: QTreeWidgetItem) -> None:
        index = self.tree.indexOfTopLevelItem(item)
        while index + 1 < self.tree.topLevelItemCount() and self.tree.topLevelItem(index + 1).text(0) == item.text(0):
            self.tree.takeTopLevelItem(index + 1)

    def get_query_parts(self, resource_name) -> list:
        query_parts = []
        root = self.tree.invisibleRootItem()
        self.traverse_tree(item=root, query_parts=query_parts, resource_name=resource_name)
        return query_parts

    def traverse_tree(self, item: QTreeWidgetItem, query_parts: list, resource_name: str) -> None:
        for i in range(item.childCount()):
            child = item.child(i)
            field = child.text(0)
            condition_widget = self.tree.itemWidget(child, 1)
            value_widget = self.tree.itemWidget(child, 2)
            if isinstance(condition_widget, QComboBox) and condition_widget.currentText() != "None":
                condition = condition_widget.currentText()
                if isinstance(value_widget, QDateTimeEdit):
                    value = value_widget.dateTime().toString(format=Qt.DateFormat.ISODate) + "Z"
                elif isinstance(value_widget, QLineEdit):
                    value = value_widget.text().lstrip("=")
                else:
                    continue
                self.add_query_part(condition, field, query_parts, value, resource_name)
            self.traverse_tree(child, query_parts, resource_name)

    def add_query_part(self, condition, field, query_parts, value, resource_name):
        if value != "":
            if condition in ["=", ">", "<", ">=", "<=", "!=", "sa", "eb", "ap"]:
                if condition == "!=":
                    value = "ne" +  value
                elif condition == ">":
                    value = "gt" + value
                elif condition == "<":
                    value = "lt" + value
                elif condition == ">=":
                    value = "ge" + value
                elif condition == "<=":
                    value = "le" + value
                elif condition == "=":
                    pass
                else:
                    value = condition + value
                condition = None
            if resource_name == "Encounter":
                query_parts.append(f"{field}:{condition}={value}") if condition and condition != "=" else query_parts.append(f"{field}={value}")
            elif resource_name == "Patient":
                query_parts.append(f"subject.{field}={value}")
            elif resource_name == "Procedure":
                query_parts.append(f"_has:Procedure:encounter:{field}:{condition}={value}") if condition and condition != "=" else query_parts.append(f"{field}={value}")
            elif resource_name == "Observation":
                query_parts.append(f"subject:_has:Observation:subject:{field}:{condition}={value}") if condition and condition != "=" else query_parts.append(f"subject:_has:Observation:subject:{field}={value}")
            elif resource_name == "Condition":
                query_parts.append(f"_has:Condition:encounter:{field}:{condition}={value}")  if condition and condition != "=" else query_parts.append(f"_has:Condition:encounter:{field}={value}")

    def request_back(self) -> None:
        self.back_requested.emit()

    def request_next(self) -> None:
        self.next_requested.emit()

    def display(self):
        self.populate_tree()
        self.show()

    def include_resource_checkbox_clicked(self):
        self.include_resource = self.include_resource_cb.isChecked()