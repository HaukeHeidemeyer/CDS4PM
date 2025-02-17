from PyQt6.QtWidgets import (
    QMainWindow, QStackedWidget
)
from .display_capability import CapabilityDisplayWidget
from .patientquery import PatientQuerySelectionWidget
from cds4py.gui.encounterquery import EncounterQuerySelectionWidget
from cds4py.gui.procedurequery import ProcedureQuerySelectionWidget
from cds4py.gui.observationquery import ObservationQuerySelectionWidget
from cds4py.gui.conditionquery import ConditionQuerySelectionWidget
from .resource_summary import ResourceSummaryWidget
from gui.utils.loading import LoadingWidget
from .select_ocel_object_source_resources import SelectResourceTypesWidget
from .object_definition import DefineObjectTypesWidget
from .select_ocel_object_relations import ObjectRelationWidget
from .event_definition import EventDefinitionWidget
from .event_resource_selection import SelectEventResourcesWidget
import logging
from .summary import SummaryWidget
from .url_input import URLInputWidget
from gui.utils.datamanager import DataManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from .controller import Controller  # Make sure to import the new Controller class


class MainWindow(QMainWindow):
    def __init__(self, debug_mode, pickle_file_path):
        super().__init__()

        self.debug_mode = debug_mode
        self.pickle_file_path = pickle_file_path

        self.setWindowTitle("FHIR Resource Query")
        self.setGeometry(100, 100, 600, 400)

        self.data_manager = DataManager()
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.init_widgets()

        # Initialize the Controller
        self.controller = Controller(self, data_manager=self.data_manager, debug_mode=self.debug_mode, pickle_file_path=self.pickle_file_path)

        self.worker = None
        self.resource_processing_worker = None

    def init_widgets(self):
        self.url_input_widget = URLInputWidget()
        self.loading_widget = LoadingWidget()
        self.resource_summary_widget = ResourceSummaryWidget()
        self.select_resource_types_widget = SelectResourceTypesWidget()
        self.capability_display_widget = CapabilityDisplayWidget()
        self.encounter_query_widget = EncounterQuerySelectionWidget()
        self.patient_query_widget = PatientQuerySelectionWidget()
        self.procedure_query_widget = ProcedureQuerySelectionWidget()
        self.condition_query_widget = ConditionQuerySelectionWidget()
        self.observation_query_widget = ObservationQuerySelectionWidget()
        self.define_object_types_widget = DefineObjectTypesWidget()
        self.object_relation_widget = ObjectRelationWidget()
        self.select_event_resources_widget = SelectEventResourcesWidget()
        self.event_definition_widget = EventDefinitionWidget()
        self.summary_widget = SummaryWidget()

        self.stack.addWidget(self.url_input_widget)
        self.stack.addWidget(self.loading_widget)
        self.stack.addWidget(self.resource_summary_widget)
        self.stack.addWidget(self.select_resource_types_widget)
        self.stack.addWidget(self.capability_display_widget)
        self.stack.addWidget(self.encounter_query_widget)
        self.stack.addWidget(self.patient_query_widget)
        self.stack.addWidget(self.procedure_query_widget)
        self.stack.addWidget(self.condition_query_widget)
        self.stack.addWidget(self.observation_query_widget)
        self.stack.addWidget(self.define_object_types_widget)
        self.stack.addWidget(self.object_relation_widget)
        self.stack.addWidget(self.select_event_resources_widget)
        self.stack.addWidget(self.event_definition_widget)
        self.stack.addWidget(self.summary_widget)

    def closeEvent(self, event):
        self.cleanup_threads()
        event.accept()

    def cleanup_threads(self):
        if self.worker and self.worker.isRunning():
            self.worker.quit()
            self.worker.wait()
        if self.resource_processing_worker and self.resource_processing_worker.isRunning():
            self.resource_processing_worker.quit()
            self.resource_processing_worker.wait()
