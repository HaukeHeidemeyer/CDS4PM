from cds4py.plugins.basecondition import BaseCondition
class NotEqualsCondition(BaseCondition):
    def __init__(self):
        super().__init__()
        self.name = "notequals"

    def evaluate(self, value, column_values):
        # value is the user input from the QLineEdit
        # column_values are the values from the column to be evaluated

        # Remove spaces from the value
        value = value.replace(" ", "")

        # Check for brackets and evaluate the expression inside the brackets first
        while "(" in value and ")" in value:
            start = value.index("(")
            end = value.rindex(")")  # Get the last occurrence of ")"
            result = self.evaluate(value[start+1:end], column_values)
            value = value[:start] + str(result) + value[end+1:]

        # Split the value based on the logical operators and evaluate each part
        or_parts = value.split(",")
        or_results = []
        for or_part in or_parts:
            and_parts = or_part.split("+")
            and_results = [str(column_values.strip()) != part for part in and_parts]
            or_results.append(all(and_results))  # Combine with logical AND

        return any(or_results)  # Combine with logical OR