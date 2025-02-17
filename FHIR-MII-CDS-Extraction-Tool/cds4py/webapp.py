import sys

sys.path.append('../')

import streamlit as st
import logging
from cds4py.utils.datamanager import DataManager
from controller import Controller
from cds4py.pages.url_input import url_input_page

class StreamlitApp:
    def __init__(self, debug_mode, pickle_file_path):
        self.debug_mode = debug_mode
        self.pickle_file_path = pickle_file_path
        self.data_manager = DataManager()
        # Initialize the controller
        self.controller = Controller(data_manager=self.data_manager, debug_mode=self.debug_mode, pickle_file_path=self.pickle_file_path)

        # Initialize the session state if not already set
        if "current_page" not in st.session_state:
            st.session_state.current_page = "URL Input"

    def run(self):
        # Streamlit allows you to create different pages or sections of your app
        st.title("FHIR Resource Query")

        # Side Navigation
        page = st.sidebar.selectbox("Select a page", [
            "URL Input", "Loading", "Resource Summary",
            "Select Resource Types", "Capability Display",
            "Encounter Query", "Patient Query",
            "Procedure Query", "Condition Query",
            "Observation Query", "Define Object Types",
            "Object Relations", "Select Event Resources",
            "Event Definition", "Summary"
        ])

        # Update the current page in session state if the sidebar selection changes
        if page != st.session_state.current_page:
            st.session_state.current_page = page

        # Render the current page
        self.render_page(st.session_state.current_page)

    def render_page(self, current_page):
        # Handling the logic for each of these pages
        if current_page == "URL Input":
            url_input_page(self.controller)  # Refactored URL Input page
        elif current_page == "Loading":
            self.loading()
        elif current_page == "Resource Summary":
            self.resource_summary()
        elif current_page == "Select Resource Types":
            self.select_resource_types()
        elif current_page == "Capability Display":
            self.capability_display()
        elif current_page == "Encounter Query":
            self.encounter_query()
        elif current_page == "Patient Query":
            self.patient_query()
        elif current_page == "Procedure Query":
            self.procedure_query()
        elif current_page == "Condition Query":
            self.condition_query()
        elif current_page == "Observation Query":
            self.observation_query()
        elif current_page == "Define Object Types":
            self.define_object_types()
        elif current_page == "Object Relations":
            self.object_relations()
        elif current_page == "Select Event Resources":
            self.select_event_resources()
        elif current_page == "Event Definition":
            self.event_definition()
        elif current_page == "Summary":
            self.summary()
        else:
            st.write("Page not found.")

    def loading(self):
        st.header("Loading...")
        st.write("Currently loading data...")

    def resource_summary(self):
        st.header("Resource Summary")
        st.write("Summary of resources goes here.")

    def select_resource_types(self):
        st.header("Select Resource Types")
        resources = ["Patients", "Encounters", "Procedures"]
        selected_resources = [res for res in resources if st.checkbox(res)]
        if st.button("Proceed"):
            response = self.controller.select_resources(selected_resources)
            st.write(response)
            if "successfully" in response:
                st.session_state.current_page = "Define Object Types"  # Move to the next page

    def capability_display(self):
        st.header("Capability Display")
        st.write("Display capability information here.")

    def encounter_query(self):
        st.header("Encounter Query")
        encounter_id = st.text_input("Enter Encounter ID:", "")
        if st.button("Submit Encounter Query"):
            response = self.controller.handle_encounter_query(encounter_id)
            st.write(response)
            if "successfully" in response:
                st.session_state.current_page = "Patient Query"  # Move to the next page

    def patient_query(self):
        st.header("Patient Query")
        patient_id = st.text_input("Enter Patient ID:", "")
        if st.button("Submit Patient Query"):
            response = self.controller.handle_patient_query(patient_id)
            st.write(response)
            if "successfully" in response:
                st.session_state.current_page = "Procedure Query"  # Move to the next page

    def procedure_query(self):
        st.header("Procedure Query")
        procedure_id = st.text_input("Enter Procedure ID:", "")
        if st.button("Submit Procedure Query"):
            response = self.controller.handle_procedure_query(procedure_id)
            st.write(response)
            if "successfully" in response:
                st.session_state.current_page = "Condition Query"  # Move to the next page

    def condition_query(self):
        st.header("Condition Query")
        condition_id = st.text_input("Enter Condition ID:", "")
        if st.button("Submit Condition Query"):
            response = self.controller.handle_condition_query(condition_id)
            st.write(response)
            if "successfully" in response:
                st.session_state.current_page = "Observation Query"  # Move to the next page

    def observation_query(self):
        st.header("Observation Query")
        observation_id = st.text_input("Enter Observation ID:", "")
        if st.button("Submit Observation Query"):
            response = self.controller.handle_observation_query(observation_id)
            st.write(response)
            if "successfully" in response:
                st.session_state.current_page = "Summary"  # Move to the next page

    def define_object_types(self):
        st.header("Define Object Types")
        st.write("Define object types here.")

    def object_relations(self):
        st.header("Object Relations")
        st.write("Define object relations here.")

    def select_event_resources(self):
        st.header("Select Event Resources")
        st.write("Select event resources here.")

    def event_definition(self):
        st.header("Event Definition")
        st.write("Define events here.")

    def summary(self):
        st.header("Summary")
        st.write("Summary of all configurations and data.")

if __name__ == '__main__':

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Debug mode
    debug_mode = True  # Set this to True to enable debug mode, False to disable
    pickle_file_path = "resources_data.pickle"

    # Create a file handler
    handler = logging.FileHandler('app.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.info("Starting the application")

    # Instantiate the Streamlit application
    app = StreamlitApp(debug_mode, pickle_file_path)

    # Run the Streamlit application
    app.run(