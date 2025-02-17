from cds4py.plugins.basemodifier import BaseModifier
class FirstNCharModifier(BaseModifier):
    def __init__(self):
        super().__init__()
        self.name = "firstnchars"
        self.restricted_to = ["Procedure", "Condition"]

    def modify(self, value, column_value):
        # value is the user input from the QLineEdit
        # column_value is the values from the column to be evaluated

        # Remove spaces from the value
        value = value.replace(" ", "")
        if not value.isdigit():
            raise ValueError("The value must be an integer", value)
        value = value.replace(" ", "")
        column_value = column_value.replace(" ", "")

        return column_value[:int(value)]