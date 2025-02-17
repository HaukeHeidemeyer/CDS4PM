"""
This script retrieves the capabilities of a FHIR server by making a GET request to the server's metadata endpoint.
"""

import requests

url = "http://localhost:8080/fhir/metadata"

response = requests.get(url)
capabilities = response.text

print(capabilities)
