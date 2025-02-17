import time

import requests
import json
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FHIRClient:
    def __init__(self, base_url, count_per_page=100, use_fhir_history=False):
        self.base_url = base_url
        self.count_per_page = count_per_page
        self.use_fhir_history = use_fhir_history

    def retrieve_all_resources(self, resource_type):
        """
        Retrieves all resources of a specified type from the FHIR server and handles paging.

        Args:
            resource_type (str): The type of the resources to retrieve.
        """
        all_resources = []
        url = f"{self.base_url}/{resource_type}?_count={self.count_per_page}"

        while url:
            response = requests.get(url)
            response.raise_for_status()
            bundle = response.json()
            resources = bundle.get('entry', [])

            for entry in resources:
                resource = entry['resource']
                resource_id = resource['id']
                all_resources.append(resource)
                if self.use_fhir_history:
                    resource_history = self.retrieve_resource_history(resource_type, resource_id)
                    all_resources.extend(resource_history)

            # Find the next URL if it exists
            url = None
            for link in bundle.get('link', []):
                if link['relation'] == 'next':
                    url = link['url']
                    break

        return all_resources

    def retrieve_resource_history(self, resource_type, resource_id):
        """
        Retrieves the history of a specific resource from the FHIR server.

        Args:
            resource_type (str): The type of the resource to retrieve.
            resource_id (str): The ID of the resource to retrieve.
        """
        all_versions = []
        url = f"{self.base_url}/{resource_type}/{resource_id}/_history"

        while url:
            response = requests.get(url)
            response.raise_for_status()
            history_bundle = response.json()
            versions = history_bundle.get('entry', [])

            for entry in versions:
                version_id = entry['resource']['meta']['versionId']
                if int(version_id) > 1:
                    all_versions.append(entry['resource'])

            # Find the next URL if it exists
            url = None
            for link in history_bundle.get('link', []):
                if link['relation'] == 'next':
                    url = link['url']
                    break

        return all_versions

    def retrieve_resource(self, resource_type, resource_id, versionId=1):
        """
        Retrieves a specific (default first) version of a resource from the FHIR server.

        Args:
            resource_type (str): The type of the resource to retrieve.
            resource_id (str): The ID of the resource to retrieve.
            versionId (int): The version of the resource to retrieve. Default is 1.
        """
        url = f"{self.base_url}/{resource_type}/{resource_id}/_history/{versionId}"
        response = requests.get(url)

        if response.status_code == 200:
            resource = response.json()
            logger.info(f"Retrieved resource: {resource}")
        elif response.status_code == 404:
            logger.error("No resource found for this id.")
        else:
            logger.error(f"Failed to retrieve the resource. Status code: {response.status_code}")

def create_update_resource(
        resource, resource_type, resource_id, base_url="http://localhost:8080/fhir", ndjson=True, retry_count=10, no_fhir_server=False
):
    """
    Creates or updates a resource with a specific ID on the FHIR server.

    Args:
        ndjson (bool): Whether to append the resource in NDJSON format to a file.
        resource (dict): The resource to create or update.
        resource_type (str): The type of the resource.
        resource_id (str): The ID of the resource.
        base_url (str): The base URL of the FHIR server.
        retry_count (int): The number of retries in case of connection errors.
    """

    headers = {"Content-Type": "application/fhir+json"}
    attempt = 0
    if ndjson:
        # Append the resource JSON to a ndjson file
        os.makedirs("output", exist_ok=True)
        with open(os.path.join("output", f"{resource_type}_resources.ndjson"), "a") as file:
            file.write(resource.json() + "\n")
        logger.debug("Resource appended to NDJSON file")
    if no_fhir_server:
        return
    while attempt < retry_count:
        try:
            if resource_id:
                url = f"{base_url}/{resource_type}/{resource_id}"
                response = requests.put(url, data=resource.json(), headers=headers)
            else:
                url = f"{base_url}/{resource_type}"
                response = requests.post(url, data=resource.json(), headers=headers)

            if response.status_code in [200, 201]:
                resource_data = response.json()
                logger.debug(f"{'Updated' if response.status_code == 200 else 'Created'} resource: {resource_data}")
                return resource_data
            else:
                logger.error(f"Failed to handle the resource. Status code: {response.status_code}, Response: {response.text}")
                return None

        except requests.ConnectionError:
            logger.error("Connection Error - the server could not be reached.")
            attempt += 1
            if attempt < retry_count:
                time.sleep(2)  # Wait before retrying
                logger.info(f"Retrying... Attempt {attempt}/{retry_count}")
            else:
                logger.error("Max retries exceeded.")
                return None
