import math

import pandas as pd
import requests
from PyQt6.QtCore import QThread, pyqtSignal
import logging
from concurrent.futures import ThreadPoolExecutor
from utils.dict import Dict

logger = logging.getLogger(__name__)

class ResourceProcessingWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, resources):
        super().__init__()
        self.resources = resources

    def flatten_resource(self, resource):
        try:
            resource_type = resource['resourceType']
            flattened_resource = Dict.flatten(resource)
            version_id = resource['meta'].get('versionId') if 'meta' in resource else None
            flattened_resource['versionId'] = version_id
            return resource_type, flattened_resource
        except Exception as e:
            logger.error(f"Error flattening resource: {e}")
            return None

    def run(self):
        try:
            resource_dataframes = {}
            total_resources = len(self.resources)

            # Using ThreadPoolExecutor for parallel processing of resources
            with ThreadPoolExecutor(max_workers=4) as executor:  # Adjust max_workers based on your CPU
                results = list(executor.map(self.flatten_resource, self.resources))

            valid_results = [result for result in results if result is not None]

            for idx, (resource_type, flattened_resource) in enumerate(valid_results):
                if resource_type not in resource_dataframes:
                    resource_dataframes[resource_type] = []
                resource_dataframes[resource_type].append(flattened_resource)

                # Emit progress at larger intervals to reduce communication overhead
                if idx % max(1, total_resources // 100) == 0:  # Emit progress every 1% processed
                    progress_percentage = int((idx + 1) / total_resources * 100)
                    self.progress.emit(progress_percentage)

            # Convert lists to pandas DataFrames
            for resource_type, data in resource_dataframes.items():
                resource_dataframes[resource_type] = pd.DataFrame(data)

            self.progress.emit(100)  # Ensure progress reaches 100%
            self.finished.emit(resource_dataframes)

        except Exception as e:
            logger.error(f"Error in ResourceProcessingWorker: {e}")
            self.error.emit(str(e))


class ResourceWorker(QThread):
    finished = pyqtSignal(list)
    progress = pyqtSignal(int)
    error = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url
        self.total_pages = None

    def run(self):
        try:
            resources = self.retrieve_all_resources(self.url)
            self.finished.emit(resources)
        except Exception as e:
            logger.error(f"Error in ResourceWorker: {e}")
            self.error.emit(str(e))

    def retrieve_all_resources(self, url, count_per_page=100):
        all_resources = []
        url = f"{url}&_count={count_per_page}" if "?" in url else f"{url}?_count={count_per_page}"
        logger.debug(f"Retrieving resources from {url}")
        page_number = 1

        while url:
            logger.info(f"Retrieving resources from {url}, page {page_number}")
            try:
                response = requests.get(url, timeout=10)  # Added a timeout to prevent hanging
                response.raise_for_status()
            except requests.RequestException as e:
                logger.error(f"Request failed: {e}")
                self.error.emit(str(e))
                return []

            bundle = response.json()
            resources = bundle.get('entry', [])

            if self.total_pages is None:
                # TODO possible bug
                total_records = int(bundle.get('total', len(resources)))
                if total_records == 0:
                    logger.warning("No resources found in the FHIR server.")
                    self.error.emit("No resources found in the FHIR server.")
                    return []
                # Correctly calculate total pages using math.ceil
                self.total_pages = math.ceil(total_records / count_per_page)

            all_resources.extend([entry['resource'] for entry in resources])

            # Calculate progress based on actual resources retrieved vs. total expected
            progress_percentage = int((len(all_resources) / total_records) * 100)
            self.progress.emit(progress_percentage)

            page_number += 1

            # Get the URL for the next page if it exists
            url = None
            for link in bundle.get('link', []):
                if link['relation'] == 'next':
                    url = link['url']
                    break

        logger.info(f"Retrieved {len(all_resources)} resources.")
        self.progress.emit(100)  # Ensure the progress bar reaches 100%
        return all_resources


class CapabilityWorker(QThread):
    finished = pyqtSignal(list)
    progress = pyqtSignal(int)
    error = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            for i in range(10):
                self.progress.emit(i + 1)
                self.msleep(100)

            capabilities = self.get_fhir_capabilities(self.url)
            self.finished.emit(capabilities)
        except Exception as e:
            logger.error(f"Error in CapabilityWorker: {e}")
            self.error.emit(str(e))

    def get_fhir_capabilities(self, base_url):
        logger.debug(f"Retrieving FHIR capabilities from {base_url}")
        url = f"{base_url}/metadata"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            self.error.emit(str(e))
            return []

        data = response.json()
        capabilities = []

        for rest in data.get('rest', []):
            capabilities.append(f"Mode: {rest.get('mode')}")
            for resource in rest.get('resource', []):
                capabilities.append(f"Resource Type: {resource.get('type')}")
                for interaction in resource.get('interaction', []):
                    capabilities.append(f"Interaction: {interaction.get('code')}")
        return capabilities
