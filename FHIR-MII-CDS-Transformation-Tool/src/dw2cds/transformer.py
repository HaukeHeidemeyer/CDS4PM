from __future__ import annotations

import logging
import os
from typing import Any

import pandas as pd
from fhir.resources import construct_fhir_element
from fhir_api.fhir_client import create_update_resource
from processor_registry import ProcessorRegistry


class FHIRTransformer:
    """
    This class represents a FHIR Transformer.
    It is used to transform data into FHIR format using field mappings and processors.
    """

    def __init__(
        self,
        field_mappings: dict[str, str],
        processor_paths: list[str | os.PathLike],
        output_data_folder_path: str,
    ):
        """
        Initializes a new instance of the FHIRTransformer class.

        Parameters:
        - field_mappings (Dict[str, str]): A dictionary containing field mappings for transforming data.
        - processor_paths (List[Union[str, os.PathLike]]): A list of paths to processor modules.

        Returns:
        - None
        """
        self.field_mappings = field_mappings
        self.processor_registry = ProcessorRegistry(processor_paths)
        self.processors = self.processor_registry.get_processors()
        self.resources = {}
        self.output_data_folder_path = output_data_folder_path

    def transform(self, row: pd.DataFrame, resource_type: str, fhir_base_url: str) -> None:
        """
        Transforms a row of data into FHIR format.

        Parameters:
        - row (pd.DataFrame): The row of data to transform.
        - resource_type (str): The resource type for the FHIR resource.

        Returns:
        - None
        """
        fhir_dict = self.field_mappings.copy().get("fields", {})
        fhir_dict = self._fill_dict(row, resource_type, fhir_dict)
        if resource_type not in self.resources:
            self.resources[resource_type] = []
            code = fhir_dict.get("code")
            if code:
                coding = fhir_dict.get("coding")
        res = construct_fhir_element(resource_type, fhir_dict)
        self._save_resource(resource_type, res, fhir_base_url)

    def _save_resource(self, resource_name, resource, fhir_base_url):
        if not os.path.exists(self.output_data_folder_path):
            os.makedirs(self.output_data_folder_path)
        with open(
            f"{self.output_data_folder_path}/{resource_name.lower()}.ndjson",
            "a",
        ) as f:
            create_update_resource(
                resource,
                resource_name,
                resource.dict().get("id"),
                base_url=fhir_base_url,
                ndjson=True,
                no_fhir_server=False,
            )

    def _create_resource(self, resource_name: str, resource_data: dict) -> Any:
        """
        Creates a FHIR resource instance based on the resource name and data.

        Parameters:
        - resource_name (str): The name of the FHIR resource.
        - resource_data (dict): The data for the FHIR resource.

        Returns:
        - Any: The created FHIR resource instance.
        """

        # Create an instance of the resource class
        resource = construct_fhir_element(resource_name.capitalize(), resource_data)

        return resource

    def _fill_dict(self, row: pd.Series, resource_type: str, mapping: dict) -> dict:
        """
        Recursively fills a dictionary with data from a row using field mappings.

        Parameters:
        - row (pd.Series): The row of data to fill the dictionary with.
        - resource_type (str): The resource type for the FHIR resource.
        - mapping (dict): The field mappings dictionary.

        Returns:
        - dict: The filled dictionary.
        """
        result = {}
        for key, val in mapping.items():
            if isinstance(val, dict):
                result[key] = self._fill_dict(row, resource_type, val)
            elif isinstance(val, list) and not isinstance(val, str):
                result = self._handle_list(key, resource_type, result, row, val)
            elif isinstance(val, str):
                if val.startswith("$") and val.endswith("$"):
                    result[key] = self._replace_processor_reference(
                        row,
                        resource_type,
                        [val.strip("$")],
                    )
                elif not val.startswith("%") and not val.endswith("%"):
                    if val.lower() != "none":
                        result[key] = val
                    else:
                        result.pop(key, None)
                elif (
                    val.startswith("%")
                    and val.endswith("%")
                    and val.strip("%") in val.strip("%") in row
                ):
                    if (
                        str(row[val.strip("%")]).lower() != "none"
                        and str(row[val.strip("%")]).lower() != "nan"
                    ):
                        result[key] = row[val.strip("%")]
                    else:
                        result.pop(key, None)
                else:
                    logging.error(f"Invalid field mapping: {val}")
                    raise ValueError(f"Invalid field mapping: {val}")
            else:
                raise ValueError(f"Invalid field mapping: {val}")
        return result

    def _handle_list(self, key, resource_type, result, row, val):
        if self._check_if_list_contains_processor_reference(val):
            res = self._replace_processor_reference(
                row,
                resource_type,
                val,
            )
            if res != "none" and res != "nan":
                result[key] = res
            else:
                result.pop(key, None)
        else:
            processed_list = []
            for item in val:
                if (
                    isinstance(item, str)
                    and item.startswith("$")
                    and item.endswith("$")
                ):
                    res = (
                        self._replace_processor_reference(
                            row,
                            resource_type,
                            [val],
                        ),
                    )

                    if res != "none" and res != "nan":
                        processed_list.append(res)
                elif isinstance(item, dict):
                    processed_list.append(
                        self._fill_dict(row, resource_type, item),
                    )
                elif isinstance(item, list):
                    processed_list.append(
                        self._handle_list(key, resource_type, result, row, item)[key],
                    )
                else:
                    if item.strip('%') not in row and item not in row:
                        raise KeyError(f"Missing column: {item}")
                    processed_list.append(str(row[item.strip('%')]))
            result[key] = processed_list
        return result

    def _check_if_list_contains_processor_reference(
        self,
        val: list[str | dict[str, str]],
    ) -> bool:
        """
        Checks if a list contains processor references.

        Parameters:
        - val (List[Union[str, Dict[str, str]]]): The list to check.

        Returns:
        - bool: True if the list contains processor references, False otherwise.
        """
        for item in val:
            if isinstance(item, str):
                if item.startswith("$") and item.endswith("$"):
                    if item.strip("$") in self.processors.keys():
                        return True
                    else:
                        raise ValueError(
                            f"Invalid processor reference: {item}",
                        )
        return False

    def _get_processor_from_list(
        self,
        val: list[str | dict[str, str]],
        resource_type: str,
    ) -> tuple:
        """
        Gets the processor and arguments from a list of processor references.

        Parameters:
        - val (List[Union[str, Dict[str, str]]]): The list of processor references.
        - resource_type (str): The resource type for the FHIR resource.

        Returns:
        - tuple: A tuple containing the processor and the remaining list of references.
        """
        for item in val:
            if isinstance(item, str):
                if item.strip("$") in self.processors.keys():
                    return self.processor_registry.get_processor(item.strip("$")), [
                        i for i in val if i != item
                    ]
        raise ValueError("No processor reference found in list")

    def _replace_processor_reference(
        self,
        row: pd.Series,
        resource_type: str,
        val: list[str | dict[str, str]],
    ) -> Any:
        """
        Replaces a processor reference with the result of the processor.

        Parameters:
        - row (pd.Series): The row of data to pass to the processor.
        - resource_type (str): The resource type for the FHIR resource.
        - val (List[Union[str, Dict[str, str]]]): The list containing the processor reference.

        Returns:
        - Any: The result of the processor.
        """
        processor, arg_names = self._get_processor_from_list(
            val,
            resource_type,
        )
        for key in arg_names:
            if not key.startswith("%") or not key.endswith("%"):
                logging.error(f"Invalid argument: {key}")
                raise ValueError(f"Invalid argument: {key}")
        args = [row[key.strip("%")] for key in arg_names]
        result = processor(*args)
        return result
