import logging
from extraction.extract import create_ocel_event_log
from pm4py import write_ocel2_json
from cds4py.fhir.fhirquery import FHIRQueryURLBuilder

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Controller:
    def __init__(self, data_manager, debug_mode, pickle_file_path):
        self.data_manager = data_manager
        self.debug_mode = debug_mode
        self.pickle_file_path = pickle_file_path

    def submit_fhir_url(self, url):
        if not url:
            logger.error("No URL provided.")
            return "No URL provided. Please enter a valid FHIR Server URL."
        logger.info(f"URL Submitted: {url}")
        self.data_manager.base_url = url
        return "URL successfully submitted"

    def select_resources(self, selected_resources):
        if not selected_resources:
            logger.error("No resources selected.")
            return "No resources selected. Please select at least one resource type."
        logger.info(f"Selected Resources: {selected_resources}")
        self.data_manager.selected_resources = selected_resources
        return "Resources successfully selected"

    def handle_encounter_query(self, encounter_id):
        if not encounter_id:
            logger.error("No Encounter ID provided.")
            return "No Encounter ID provided. Please enter a valid Encounter ID."
        logger.info(f"Encounter ID Submitted: {encounter_id}")
        return "Encounter ID successfully processed"

    def handle_patient_query(self, patient_id):
        if not patient_id:
            logger.error("No Patient ID provided.")
            return "No Patient ID provided. Please enter a valid Patient ID."
        logger.info(f"Patient ID Submitted: {patient_id}")
        return "Patient ID successfully processed"

    def handle_procedure_query(self, procedure_id):
        if not procedure_id:
            logger.error("No Procedure ID provided.")
            return "No Procedure ID provided. Please enter a valid Procedure ID."
        logger.info(f"Procedure ID Submitted: {procedure_id}")
        return "Procedure ID successfully processed"

    def handle_condition_query(self, condition_id):
        if not condition_id:
            logger.error("No Condition ID provided.")
            return "No Condition ID provided. Please enter a valid Condition ID."
        logger.info(f"Condition ID Submitted: {condition_id}")
        return "Condition ID successfully processed"

    def handle_observation_query(self, observation_id):
        if not observation_id:
            logger.error("No Observation ID provided.")
            return "No Observation ID provided. Please enter a valid Observation ID."
        logger.info(f"Observation ID Submitted: {observation_id}")
        return "Observation ID successfully processed"

    def load_resources(self, url):
        self.data_manager.base_url = url
        logger.info(f"Loading resources from URL: {url}")
        # Here you would load resources using some HTTP requests or data extraction logic
        # For now, just proceed to indicate loading is in progress
        return "Loading resources from URL"

    def handle_extraction(self):
        # Perform OCEL event log creation
        try:
            ocel = create_ocel_event_log(self.data_manager.query_data, self.data_manager.defined_objects,
                                         self.data_manager.defined_events, self.data_manager.defined_relations)
            write_ocel2_json(ocel, "outputocel.jsonocel")
            logger.info("Extraction process completed successfully.")
            return "The extraction process completed successfully."
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            return "The extraction process failed."

    def handle_query_construction(self):
        # Construct the FHIR query URL
        url_builder = FHIRQueryURLBuilder(self.data_manager.base_url)
        # Assuming each widget has methods to get the query parts
        encounter_query = self.data_manager.get_query_parts("Encounter")
        patient_query = self.data_manager.get_query_parts("Patient")
        procedure_query = self.data_manager.get_query_parts("Procedure")
        condition_query = self.data_manager.get_query_parts("Condition")
        observation_query = self.data_manager.get_query_parts("Observation")

        for part in encounter_query + patient_query + procedure_query + condition_query + observation_query:
            url_builder.add_query_part(part)

        query_url = url_builder.build_url()
        self.data_manager.fhir_query = query_url
        logger.info(f"Constructed FHIR Query URL: {query_url}")
        return f"Constructed FHIR Query URL: {query_url}"
