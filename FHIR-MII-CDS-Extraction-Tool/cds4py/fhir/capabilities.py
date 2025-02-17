import requests

def get_fhir_capabilities(base_url):
    # Construct the URL for the metadata endpoint
    url = f"{base_url}/metadata"

    # Send a GET request to the metadata endpoint
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        capabilities = []

        # The capabilities are listed under 'rest' in the 'CapabilityStatement' resource
        for rest in data.get('rest', []):
            capabilities.append(f"Mode: {rest.get('mode')}")
            for resource in rest.get('resource', []):
                capabilities.append(f"Resource Type: {resource.get('type')}")
                for interaction in resource.get('interaction', []):
                    capabilities.append(f"Interaction: {interaction.get('code')}")
        return capabilities
    else:
        return [f"Failed to get capabilities: {response.status_code}, {response.text}"]
