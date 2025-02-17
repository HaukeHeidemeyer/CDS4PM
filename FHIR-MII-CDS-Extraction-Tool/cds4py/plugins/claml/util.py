import xml.etree.ElementTree as ET
import re


class XMLResolver:
    def __init__(self, claml_file):
        # Load and parse the XML file
        self.tree = ET.parse(claml_file)
        self.root = self.tree.getroot()

    def resolve_code(self, value, range=False):
        found = None
        code_found = False  # Flag to indicate when the code is found

        # Iterate through each Class element (for exact matches)
        for cls in self.root.findall(".//Class"):
            if code_found:  # Break outer loop if code has been found
                break
            # Check if the current class code exactly matches the provided value
            if cls.get('code') == value:
                resolved = self._extract_rubrics(cls)
                found = " | ".join(resolved)
                code_found = True
                break

        if found is None and range:
            # If no exact match, search through ranges in chapters or blocks
            for cls in self.root.findall(".//Class[@kind='chapter']"):
                for subclass in cls.findall("SubClass"):
                    subclass_code = subclass.get('code')
                    if "-" in subclass_code:
                        range_start, range_end = subclass_code.split("-")

                        # Check if the value falls within the subclass range
                        if range_start <= value <= range_end:
                            # Narrow down to the specific category inside this chapter
                            found = self._resolve_in_range(value, range_start, range_end)
                            code_found = True
                            break

                if code_found:
                    break

        if found is None:
            raise ValueError(f"Code {value} not found in the CLAML file")

        return found

    def _resolve_in_range(self, value, range_start, range_end):
        """
        Helper function to narrow down the code resolution within a range.
        """
        resolved = []
        # Check the specific categories under the identified block
        for cls in self.root.findall(f".//Class[@kind='block']"):
            if cls.get('code') == f"{range_start}-{range_end}":
                # Search within this block for exact categories (e.g., A00, A01)
                for subclass in cls.findall("SubClass"):
                    if subclass.get('code') == value:
                        resolved = self._extract_rubrics(subclass)
                        return " | ".join(resolved)

        return "unknown"

    def _extract_rubrics(self, cls):
        """
        Extracts rubrics (labels) from a Class or SubClass element.
        """
        resolved = []
        # Iterate through each Rubric in the class
        found = False
        for rubric in cls.findall('Rubric'):
            # Find the Label element within the Rubric
            if found:
                break
            for label in rubric.findall('Label'):
                # Extract the text content from the Label element
                label_text = label.text
                if label_text:
                    resolved.append(label_text)
                    found = True
                    break
        return resolved


if __name__ == "__main__":
    # Usage example
    resolver = XMLResolver("icd10gm2020syst_claml_20190920.xml")

    # Exact code resolution
    try:
        print(resolver.resolve_code("A00.0", range=True))
    except ValueError as e:
        print(e)

    # Range code resolution
    try:
        print(resolver.resolve_code("A00", range=True))
    except ValueError as e:
        print(e)
