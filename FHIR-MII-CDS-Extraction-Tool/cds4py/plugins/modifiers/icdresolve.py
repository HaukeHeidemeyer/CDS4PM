import os
import logging
import re
from cds4py.plugins.claml.util import XMLResolver
from cds4py.plugins.basemodifier import BaseModifier

logger = logging.getLogger(__name__)

class ICDCodesResolver:

    def __init__(self):
        super().__init__()
        self.name = "icdcoderesolver"
        self.restricted_to = ["Diagnosis"]
        # Initialize XMLResolver with the correct ICD XML file path
        self.xml_resolver = XMLResolver(os.path.join(os.path.dirname(__file__), "../claml/icd10gm2020syst_claml_20190920.xml"))

    def modify(self, value, column_value):
        # value is the user input from the QLineEdit
        # column_value is the values from the column to be evaluated

        # Remove spaces from the value
        value = value.replace(" ", "")

        # Regex pattern to match ICD codes
        # ICD codes can have a structure like "A00.0" or "B00.10"
        icd_code_pattern = r"[A-Z]\d{2}\.\d{1,2}"

        # Check if the provided code matches the ICD format
        match = re.match(icd_code_pattern, column_value)

        # Remove last n letters of ICD code
        column_value = column_value[:int(value)]
        # Length of ICD codes can be 3 to 6 characters
        column_value_cleaned = column_value.removesuffix(".").removesuffix("0")

        if len(column_value_cleaned) == 1:
            column_value_cleaned = column_value_cleaned + "00"
        if len(column_value_cleaned) not in [3, 5, 6] or not match:
            return "unknown " + column_value

        try:
            # Initialize the result list
            results = []

            # Handle different lengths of ICD codes
            max_len = min(len(column_value_cleaned), 6)  # If shorter than 6, stop at max length
            for length in [3, max_len]:
                if length <= max_len:
                    # Try resolving the code for the current length
                    try:
                        result = self.xml_resolver.resolve_code(column_value_cleaned[:length], range=True)
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
    icd_resolver = ICDCodesResolver()
    print(icd_resolver.modify("6", "A00"))
