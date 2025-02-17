import requests

base_url = "http://localhost:8080/fhir/"
metadata_url = f"{base_url}/metadata"
resource_counts = {}

# Fetch CapabilityStatement
capability_statement = requests.get(metadata_url).json()
resources = capability_statement['rest'][0]['resource']

# Count resources for each type
for resource in resources:
    resource_type = resource['type']
    count_url = f"{base_url}/{resource_type}?_summary=count"
    response = requests.get(count_url).json()
    resource_counts[resource_type] = response.get('total', 0)

# Print the counts
for resource_type, count in resource_counts.items():
    print(f"{resource_type}: {count}")
