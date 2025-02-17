from cds4py.extraction.extract import create_ocel_event_log
from pm4py import write_ocel2_json

import pickle
import os
import datetime
import subprocess

import logging
from PyQt6.QtWidgets import QMessageBox
from .resource_worker import CapabilityWorker, ResourceWorker, ResourceProcessingWorker
from cds4py.fhir.fhirquery import FHIRQueryURLBuilder
from cds4py.configuration.manager import ConfigurationManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
OUTPUT_FOLDER = "output"

class Controller:
    def __init__(self, main_window, data_manager, debug_mode, pickle_file_path):
        self.main_window = main_window
        self.data_manager = data_manager
        self.debug_mode = debug_mode
        self.pickle_file_path = pickle_file_path

        self.init_connections()

    def init_connections(self):
        # Connect signals from the views (widgets) to controller methods
        self.main_window.url_input_widget.url_submitted.connect(self.show_encounter)
        self.main_window.url_input_widget.show_capabilities.connect(self.load_capabilities)
        self.main_window.url_input_widget.configuration_loaded.connect(self.handle_configuration_loaded)

        self.main_window.resource_summary_widget.back_requested.connect(self.show_url_input)
        self.main_window.resource_summary_widget.next_requested.connect(self.show_select_resource_types)

        self.main_window.select_resource_types_widget.back_requested.connect(self.show_resource_summary)
        self.main_window.select_resource_types_widget.next_requested.connect(self.show_define_object_types)

        self.main_window.capability_display_widget.back_requested.connect(self.show_url_input)

        self.main_window.encounter_query_widget.back_requested.connect(self.show_url_input)
        self.main_window.encounter_query_widget.next_requested.connect(self.show_patient)

        self.main_window.patient_query_widget.back_requested.connect(self.show_encounter)
        self.main_window.patient_query_widget.next_requested.connect(self.show_procedure)

        self.main_window.procedure_query_widget.back_requested.connect(self.show_patient)
        self.main_window.procedure_query_widget.next_requested.connect(self.show_condition)
        self.main_window.condition_query_widget.back_requested.connect(self.show_procedure)
        self.main_window.condition_query_widget.next_requested.connect(self.show_observation)

        self.main_window.observation_query_widget.back_requested.connect(self.show_condition)
        self.main_window.observation_query_widget.next_requested.connect(self.show_query)

        self.main_window.define_object_types_widget.back_requested.connect(self.show_select_resource_types)
        self.main_window.define_object_types_widget.next_requested.connect(self.show_object_relations)

        self.main_window.object_relation_widget.relations_defined.connect(self.store_relations)
        self.main_window.object_relation_widget.next_requested.connect(self.show_select_event_resources)
        self.main_window.object_relation_widget.back_requested.connect(self.back_to_define_object_types)

        self.main_window.select_event_resources_widget.back_requested.connect(self.back_to_object_relations)
        self.main_window.select_event_resources_widget.next_requested.connect(self.show_event_definition)

        self.main_window.event_definition_widget.back_requested.connect(self.show_select_event_resources)
        self.main_window.event_definition_widget.event_defined.connect(self.show_summary_widget)

        self.main_window.summary_widget.back_requested.connect(self.back_to_event_definition)
        self.main_window.summary_widget.start_extraction_requested.connect(self.start_extraction)

    def show_url_input(self):
        self.main_window.stack.setCurrentWidget(self.main_window.url_input_widget)

    def show_encounter(self):
        if self.debug_mode and os.path.isfile(self.pickle_file_path):
            with open(self.pickle_file_path, "rb") as file:
                self.data_manager.query_data = pickle.load(file)
            resource_dataframes = self.data_manager.query_data
            resource_counts = {resource_type: len(df) for resource_type, df in resource_dataframes.items()}
            self.main_window.resource_summary_widget.display_resource_counts(resource_counts)
            self.main_window.stack.setCurrentWidget(self.main_window.resource_summary_widget)
            return
        self.data_manager.base_url = self.main_window.url_input_widget.url_entry.text()
        self.main_window.stack.setCurrentWidget(self.main_window.encounter_query_widget)

    def load_resources(self, url, show_summary=True):
        self.data_manager.base_url = url
        self.main_window.stack.setCurrentWidget(self.main_window.loading_widget)

        self.main_window.cleanup_threads()  # Clean up any existing threads before starting a new one
        self.main_window.worker = ResourceWorker(url)
        self.main_window.worker.progress.connect(self.main_window.loading_widget.update_progress)
        self.main_window.worker.finished.connect(lambda resources: self.handle_resource_loaded(resources, show_summary))
        self.main_window.worker.error.connect(self.handle_resource_load_error)
        self.main_window.worker.start()

    def handle_resource_loaded(self, resources, show_summary):
        self.main_window.cleanup_threads()  # Clean up any existing threads before starting a new one
        self.main_window.resource_processing_worker = ResourceProcessingWorker(resources)
        self.main_window.resource_processing_worker.progress.connect(self.main_window.loading_widget.update_progress)
        self.main_window.resource_processing_worker.finished.connect(
            lambda resource_dataframes: self.handle_resource_processed(resource_dataframes, show_summary))
        self.main_window.resource_processing_worker.error.connect(self.handle_resource_load_error)
        self.main_window.resource_processing_worker.start()

    def handle_resource_processed(self, resource_dataframes, show_summary):
        if self.debug_mode and not os.path.isfile(self.pickle_file_path):
            with open(self.pickle_file_path, "wb") as file:
                pickle.dump(resource_dataframes, file)

        self.data_manager.query_data = resource_dataframes
        resource_counts = {resource_type: len(df) for resource_type, df in resource_dataframes.items()}

        if show_summary:
            self.main_window.resource_summary_widget.display_resource_counts(resource_counts)
            self.main_window.stack.setCurrentWidget(self.main_window.resource_summary_widget)
        else:
            self.main_window.summary_widget.set_data(self.data_manager)
            self.main_window.stack.setCurrentWidget(self.main_window.summary_widget)

    def show_resource_summary(self):
        resource_dataframes = self.data_manager.query_data
        resource_counts = {resource_type: len(df) for resource_type, df in resource_dataframes.items()}
        self.main_window.resource_summary_widget.display_resource_counts(resource_counts)
        self.main_window.stack.setCurrentWidget(self.main_window.resource_summary_widget)

    def handle_resource_load_error(self, error_message):
        QMessageBox.critical(self.main_window, "Error", f"Failed to load resources: {error_message}")
        self.show_observation()

    def load_capabilities(self, url):
        self.main_window.stack.setCurrentWidget(self.main_window.capability_display_widget)

        self.main_window.worker = CapabilityWorker(url)
        self.main_window.worker.progress.connect(self.main_window.capability_display_widget.update_progress)
        self.main_window.worker.finished.connect(self.main_window.capability_display_widget.display_capabilities)
        self.main_window.worker.error.connect(self.main_window.capability_display_widget.display_error)
        self.main_window.worker.start()

    def show_patient(self):
        self.main_window.stack.setCurrentWidget(self.main_window.patient_query_widget)

    def show_procedure(self):
        self.main_window.stack.setCurrentWidget(self.main_window.procedure_query_widget)

    def show_condition(self):
        self.main_window.stack.setCurrentWidget(self.main_window.condition_query_widget)

    def show_observation(self):
        self.main_window.stack.setCurrentWidget(self.main_window.observation_query_widget)

    def show_query(self):
        url_builder = FHIRQueryURLBuilder(self.data_manager.base_url)

        encounter_query = self.main_window.encounter_query_widget.get_query_parts("Encounter")
        patient_query = self.main_window.patient_query_widget.get_query_parts("Patient")
        procedure_query = self.main_window.procedure_query_widget.get_query_parts("Procedure")
        condition_query = self.main_window.condition_query_widget.get_query_parts("Condition")
        observation_query = self.main_window.observation_query_widget.get_query_parts("Observation")

        for part in encounter_query + patient_query + procedure_query + condition_query + observation_query:
            url_builder.add_query_part(part)

        if self.main_window.patient_query_widget.include_resource:
            url_builder.include_resource("Encounter", "subject")
        if self.main_window.procedure_query_widget.include_resource:
            url_builder.rev_include_resource("Procedure", "encounter")
        if self.main_window.condition_query_widget.include_resource:
            url_builder.rev_include_resource("Condition", "encounter")
        if self.main_window.observation_query_widget.include_resource:
            url_builder.rev_include_resource("Observation", "encounter")
        if self.main_window.observation_query_widget.include_resource:
            url_builder.rev_include_resource("Consent", "encounter")

        query_url = url_builder.build_url()
        self.data_manager.fhir_query = query_url
        self.load_resources(query_url)

    def show_select_resource_types(self):
        resource_counts = {resource_type: len(df) for resource_type, df in self.data_manager.query_data.items()}
        self.main_window.select_resource_types_widget.populate_checkboxes(resource_counts, self.data_manager.selected_resources)
        self.main_window.stack.setCurrentWidget(self.main_window.select_resource_types_widget)

    def show_define_object_types(self, selected_resources):
        self.data_manager.selected_resources = selected_resources
        self.main_window.define_object_types_widget.set_resource_tables(self.data_manager.query_data)
        self.main_window.define_object_types_widget.update_selected_resources(selected_resources)
        self.main_window.stack.setCurrentWidget(self.main_window.define_object_types_widget)

    def show_object_relations(self):
        self.data_manager.defined_objects = self.main_window.define_object_types_widget.get_all_object_definitions()
        logger.debug(f"Defined Objects in show_object_relations: {self.data_manager.defined_objects}")

        self.main_window.object_relation_widget.set_data(
            object_definitions=self.data_manager.defined_objects,
            plugins=self.main_window.define_object_types_widget.plugins,
            resource_tables=self.data_manager.query_data
        )
        self.main_window.stack.setCurrentWidget(self.main_window.object_relation_widget)

    def store_relations(self, relations):
        self.data_manager.object_relations = relations
        logger.debug(f"Stored Object Relations in DataManager: {relations}")

    def show_select_event_resources(self):
        resource_counts = {resource_type: len(df) for resource_type, df in self.data_manager.query_data.items()}
        self.main_window.select_event_resources_widget.populate_checkboxes(resource_counts, self.data_manager.selected_event_resources)
        self.main_window.stack.setCurrentWidget(self.main_window.select_event_resources_widget)

    def show_event_definition(self, selected_resources):
        self.data_manager.selected_event_resources = selected_resources
        self.main_window.event_definition_widget.set_data(self.data_manager.selected_event_resources, self.data_manager.query_data, self.data_manager.defined_objects)
        self.main_window.stack.setCurrentWidget(self.main_window.event_definition_widget)

    def show_summary_widget(self, event_definitions):
        self.data_manager.defined_events = event_definitions
        self.main_window.summary_widget.set_data(self.data_manager)
        self.main_window.stack.setCurrentWidget(self.main_window.summary_widget)

    def back_to_define_object_types(self):
        self.show_define_object_types(self.data_manager.selected_resources)

    def back_to_object_relations(self):
        self.show_object_relations()

    def back_to_event_definition(self):
        self.show_event_definition(self.data_manager.selected_event_resources)

    def start_extraction(self):
        cfgmgr = ConfigurationManager(self.data_manager.defined_objects, self.data_manager.defined_events,
                                      self.data_manager.object_relations, self.data_manager.fhir_query)

        os.makedirs(OUTPUT_FOLDER, exist_ok=True)

        datetime_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        config_file_name = f"configuration_{datetime_str}.json"
        path = os.path.join(OUTPUT_FOLDER, config_file_name)
        cfgmgr.save_to_file(path)

        ocel = create_ocel_event_log(self.data_manager.query_data, self.data_manager.defined_objects,
                                     self.data_manager.defined_events, self.data_manager.object_relations)
        logger.debug(f"Defined Objects passed to create_ocel_event_log: {self.data_manager.defined_objects}")

        path = os.path.join(OUTPUT_FOLDER, f"ocel_{datetime_str}.jsonocel")
        write_ocel2_json(ocel, path)
        QMessageBox.information(self.main_window, "Extraction Completed",
                                "The extraction process completed successfully.")

        subprocess.Popen(['xdg-open', OUTPUT_FOLDER])

    def handle_configuration_loaded(self, config_data):
        self.data_manager.defined_objects = config_data.get('defined_objects', {})
        self.data_manager.defined_events = config_data.get('defined_events', {})
        self.data_manager.object_relations = config_data.get('defined_relations', {})
        self.data_manager.fhir_query = config_data.get('fhir_query', '')

        if self.data_manager.fhir_query:
            self.load_resources(self.data_manager.fhir_query, show_summary=False)
        else:
            QMessageBox.warning(self.main_window, "Configuration Error",
                                "FHIR query URL is missing in the configuration.")

        print("Configuration loaded successfully")
