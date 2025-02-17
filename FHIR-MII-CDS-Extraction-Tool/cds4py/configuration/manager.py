import json
import logging
logger = logging.getLogger(__name__)

class ConfigurationManager:
    def __init__(self, defined_objects=None, defined_events=None, defined_o2o_relations=None, fhir_query=None):
        self.defined_objects = defined_objects or {}
        self.defined_events = defined_events or {}
        self.defined_o2o_relations = defined_o2o_relations or {}
        self.fhir_query = fhir_query or ""

    def save_to_file(self, file_path):
        """Save configuration to a JSON file."""
        try:
            config_data = {
                "defined_objects": self.defined_objects,
                "defined_events": self.defined_events,
                "defined_o2o_relations": self.defined_o2o_relations,
                "fhir_query": self.fhir_query,
            }
            with open(file_path, "w") as json_file:
                json.dump(config_data, json_file, indent=4)
            logger.info(f"Configuration saved to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration to file: {e}")
            raise

    @classmethod
    def load_from_file(cls, file_path):
        """Load configuration from a JSON file."""
        try:
            with open(file_path, "r") as json_file:
                config_data = json.load(json_file)
            logger.info(f"Configuration loaded from {file_path}")
            return cls(
                defined_objects=config_data.get("defined_objects"),
                defined_events=config_data.get("defined_events"),
                defined_o2o_relations=config_data.get("defined_o2o_relations"),
                fhir_query=config_data.get("fhir_query"),
            )
        except Exception as e:
            logger.error(f"Failed to load configuration from file: {e}")
            raise