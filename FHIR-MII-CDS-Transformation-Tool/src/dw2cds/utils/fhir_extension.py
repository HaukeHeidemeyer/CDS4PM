from __future__ import annotations

from datetime import datetime

from fhir.resources.extension import Extension
from fhir.resources.fhirtypes import Uri


def create_extension(url: str, value):
    """
    Creates an Extension instance with the provided URL and value.

    Args:
        url (str): The URL of the extension.
        value (str): The value of the extension.

    Returns: fhir.resources.extension.Extension: The created Extension instance.
    """
    extension = Extension.construct()
    extension.url = Uri(url)
    if isinstance(value, str):
        extension.valueString = value
    if isinstance(value, datetime):
        extension.valueDateTime = value
    return extension
