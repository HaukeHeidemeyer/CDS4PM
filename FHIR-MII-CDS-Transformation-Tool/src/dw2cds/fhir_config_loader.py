from __future__ import annotations

import json
import logging
import os
import sys


class FHIRConfigLoader:
    """
    A class for loading FHIR configuration from a file.

    Args:
        config_path (os.PathLike | str): The path to the configuration file.

    Attributes:
        mapping_path (os.PathLike | str): The path to the configuration file.
        config (dict): The loaded configuration.
        table_names (dict_keys): The names of the tables loaded from the configuration.

    """

    def __init__(self, config_path: os.PathLike | str):
        """
        Initialize the FHIRConfigLoader instance.

        Args:
            config_path (os.PathLike | str): The path to the configuration file.

        """
        self.mapping_path = config_path
        self.config = self._load_config()
        self.table_names = self._load_table_names()

    def load_mappings(self) -> dict[str, str | list[str] | dict]:
        """
        Load the resource mappings from the configuration.

        Returns:
            dict[str, str | list[str] | dict]: The resource mappings.

        Raises:
            SystemExit: If no resource mappings are found in the configuration file.

        """
        mappings = self.config.get("resourceMappings", {}) if self.config else {}
        if not mappings:
            logging.critical(
                f"No resource mappings found in the config file in path {self.mapping_path}",
            )
            sys.exit(1)
        return mappings.copy()

    def load_processors(self) -> dict[str, list[str]]:
        """
        Load the processors from the configuration.

        Returns:
            dict[str, list[str]]: The processors.

        """
        processors = {}
        if self.config:
            mappings = self.config.get("resourceMappings", [])
            for mapping in mappings:
                fields = mapping.get("fields", {})
                for field, value in fields.items():
                    if isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict):
                                for sub_value in item.values():
                                    if (
                                        isinstance(sub_value, str)
                                        and sub_value.startswith("$")
                                        and sub_value.endswith("$")
                                    ):
                                        processors[sub_value] = []
                            elif (
                                isinstance(item, str)
                                and item.startswith("$")
                                and item.endswith("$")
                            ):
                                processors[item.strip("$")] = []
                    elif (
                        isinstance(value, str)
                        and value.startswith("$")
                        and value.endswith("$")
                    ):
                        processors[value.strip("$")] = []
        return processors

    def _load_config(self) -> dict:
        """
        Load the configuration from the file.

        Returns:
            dict: The loaded configuration.

        Raises:
            FileNotFoundError: If the configuration file is not found.

        """
        try:
            with open(self.mapping_path) as file:
                return json.load(file)
        except FileNotFoundError:
            logging.critical(f"Config file not found in path {self.mapping_path}")
            sys.exit(1)

    def _load_table_names(self):
        """
        Load the table names from the configuration.

        Returns:
            dict_keys: The names of the tables loaded from the configuration.

        """
        return self.config.get("table_loader").keys()


if __name__ == "__main__":
    mapping_path = os.path.join(
        os.getcwd(),
        "..",
        "tests",
        "data",
        "mock_FHIR_config.json",
    )
    loader = FHIRConfigLoader(mapping_path)
    mappings = loader.load_mappings()
    processors = loader.load_processors()