class DataManager:
    def __init__(self):
        self.query_data = None
        self.selected_resources = []
        self.defined_relations = {}
        self.defined_events = {}
        self.defined_objects = {}
        self.selected_event_resources = []
        self.fhir_query = ""