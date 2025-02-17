import os
import logging
import re
from cds4py.plugins.claml.util import XMLResolver
from cds4py.plugins.basemodifier import BaseModifier

logger = logging.getLogger(__name__)

class OPSCodesResolver:

    def __init__(self):
        super().__init__()
        self.name = "opscoderesolver"
        self.restricted_to = ["Procedure"]
        # Initialize XMLResolver with the correct file path
        self.xml_resolver = XMLResolver(os.path.join(os.path.dirname(__file__), "../claml/ops2019syst_claml_20181019.xml"))

    def modify(self, value, column_value):
        # value is the user input from the QLineEdit
        # column_value is the values from the column to be evaluated

        # Remove spaces from the value
        value = value.replace(" ", "")

        if not value.isdigit():
            raise ValueError("The value must be an integer")

        # Regex pattern to match OPS codes
        ops_code_pattern = r"(\d{1,2}-\d{1,3}\.\d{1,2})|(\d{1,2}\.\d{2}\.\d{1,2})"

        # Check if the provided code matches the OPS format
        match = re.match(ops_code_pattern, column_value)

        # Remove last n letters of ops code
        column_value = column_value[:int(value)]
        # Length of ops codes is limited and with "." and "-" determined
        column_value_cleaned = column_value.removesuffix(".").removesuffix("-")

        if len(column_value_cleaned) not in [1, 4, 5, 7] or not match:
            return "unknown " + column_value

        try:
            # Initialize the result list
            results = []

            # Handle the case where length is 7
            max_len = min(len(column_value_cleaned), 7)  # If shorter than 7, stop at max length
            for length in [1, 4, 5, 7]:
                if length <= max_len:
                    # Try resolving the code for the current length
                    try:
                        result = self.xml_resolver.resolve_code(column_value_cleaned[:length])
                        results.append(result)
                    except ValueError:
                        # If code for this length is not found, skip it
                        results.append(f"unknown ({column_value_cleaned[:length]})")

            # Join all resolved parts and return the final result
            return " | ".join(results)

        except ValueError:
            return "unknown " + column_value


if __name__ == "__main__":
    # Usage example
    ops_resolver = OPSCodesResolver()
    print(ops_resolver.modify("4", "1-650.1"))
