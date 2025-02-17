from datetime import datetime
from cds4py.plugins.basecondition import BaseCondition

class DateRangeCondition(BaseCondition):
    def __init__(self):
        super().__init__()
        self.name = "daterange"

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
            and_results = []
            for part in and_parts:
                # Split the part into start and end dates
                start_date_str, end_date_str = part.split("-")
                # Convert the dates to datetime objects
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                # Check if the column_values fall within the date range
                and_results.append(start_date <= column_values <= end_date)
            or_results.append(all(and_results))  # Combine with logical AND

        return any(or_results)  # Combine with logical OR