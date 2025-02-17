import json
import logging
import os
import requests
from tqdm import tqdm
from typing import Union
from gui.utils.loading import LoadingWidget
# Configure logging
logger = logging.getLogger(__name__)

class FHIRClient:
    def __init__(self, base_url, count_per_page=100, use_fhir_history=False):
        self.base_url = base_url
        self.count_per_page = count_per_page
        self.use_fhir_history = use_fhir_history

    def retrieve_all_resources(self, url):
        """
        Retrieves all resources of a specified type from the FHIR server and handles paging.

        Args:
            resource_type (str): The type of the resources to retrieve.
        """
        all_resources = []
        url = f"{url}&_count={self.count_per_page}" if "?" in url else f"{url}?_count={self.count_per_page}"
        logger.info(f"Retrieving resources from {url}")

        page_number = 1
        total_pages = None
        with tqdm(desc="Retrieving pages", unit="page") as pbar:
            while url:
                response = requests.get(url)
                response.raise_for_status()
                bundle = response.json()
                resources = bundle.get('entry', [])

                if total_pages is None:
                    total_records = int(bundle.get('total', len(resources)))
                    total_pages = (total_records // self.count_per_page) + (total_records % self.count_per_page > 0)
                    logger.info(f"Total pages: {total_pages} in {total_records} records.")
                    pbar.total = total_pages
                    lw = LoadingWidget(total_pages)
                    lw.show()


                for entry in resources:
                    resource_type = entry['resource']['resourceType']
                    resource = entry['resource']
                    resource_id = resource['id']
                    all_resources.append(resource)
                    if self.use_fhir_history:
                        resource_history = self.retrieve_resource_history(resource_type, resource_id)
                        all_resources.extend(resource_history)

                # Update progress bar
                pbar.update(1)
                page_number += 1
                lw.update_progress(page_number)

                # Find the next URL if it exists
                url = None
                for link in bundle.get('link', []):
                    if link['relation'] == 'next':
                        url = link['url']
                        break

        logger.info("Finished retrieving resources.")
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
        logger.info(f"Retrieving history for {resource_type} with ID {resource_id}")

        while url:
            response = requests.get(url)
            response.raise_for_status()
            history_bundle = response.json()
            versions = history_bundle.get('entry', [])

            for entry in tqdm(versions, desc="Processing resource history", unit="version"):
                version_id = entry['resource']['meta']['versionId']
                if int(version_id) > 1:
                    all_versions.append(entry['resource'])

            # Find the next URL if it exists
            url = None
            for link in history_bundle.get('link', []):
                if link['relation'] == 'next':
                    url = link['url']
                    break

        logger.info(f"Finished retrieving history for {resource_type} with ID {resource_id}")
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
        logger.info(f"Retrieving resource from {url}")

        if response.status_code == 200:
            resource = response.json()
            logger.info(f"Retrieved resource: {resource}")
        elif response.status_code == 404:
            logger.error("No resource found for this id.")
        else:
            logger.error(f"Failed to retrieve the resource. Status code: {response.status_code}")

    def create_update_resource(self, resource, resource_type, resource_id, ndjson=False):
        """
        Creates or updates a resource with a specific ID on the FHIR server.

        Args:
            resource (dict): The resource to create or update.
            resource_type (str): The type of the resource.
            resource_id (str): The ID of the resource.
        """
        url = f"{self.base_url}/{resource_type}/{resource_id}"
        headers = {"Content-Type": "application/fhir+json"}
        logger.info(f"Creating/updating resource at {url}")

        if not ndjson:
            response = requests.put(url, data=json.dumps(resource), headers=headers)

            if response.status_code == 200:
                resource = response.json()
                logger.info(f"Updated resource: {resource}")
            elif response.status_code == 201:
                resource = response.json()
                logger.info(f"Created resource: {resource}")
            elif response.status_code == 400:
                logger.error(
                    "Bad Request - resource could not be parsed or failed basic FHIR validation rules (or multiple matches were found for conditional criteria)."
                )
            elif response.status_code == 401:
                logger.error(
                    "Unauthorized - authorization is required for the interaction that was attempted."
                )
            elif response.status_code == 404:
                logger.error("Not Found - resource type not supported, or not a FHIR end-point.")
            elif response.status_code == 405:
                logger.error(
                    "Method Not Allowed - the resource did not exist prior to the update, and the server does not allow client defined ids."
                )
            elif response.status_code == 409 or response.status_code == 412:
                logger.error("Conflict/Precondition Failed - version conflict management.")
            elif response.status_code == 422:
                logger.error("Unprocessable Entity.")
            else:
                logger.error(f"Failed to retrieve the resource. Status code: {response.status_code}")
        else:
            # Append the resource JSON to a ndjson file
            with open(f"{resource_type}_resources.ndjson", "a") as file:
                file.write(json.dumps(resource) + "\n")
            logger.info(f"Appended resource to {resource_type}_resources.ndjson")


def main():
    base_url = "http://localhost:8080/fhir"
    resource_type = "Patient"
    count_per_page = 100
    use_fhir_history = True

    fhir_client = FHIRClient(base_url, count_per_page, use_fhir_history)
    resources = fhir_client.retrieve_all_resources(f"{base_url}/{resource_type}")

    for resource in resources:
        print(json.dumps(resource, indent=2))


if __name__ == "__main__":
    main()
