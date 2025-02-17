from gui.resourcefieldqueryselection import ResourceFieldQuerySelection


class ProcedureQuerySelectionWidget(ResourceFieldQuerySelection):

    def __init__(self):
        self.resource_name = "Procedure"
        super().__init__("Procedure")

    def get_parameters(self):
        return {
            "based-on": "reference",
            "category": "token",
            "code": "token",
            "date": "date",
            "encounter": "reference",
            "identifier": "token",
            "instantiates-canonical": "reference",
            "instantiates-uri": "uri",
            "location": "reference",
            "part-of": "reference",
            "patient": "reference",
            "performer": "reference",
            "reason-code": "token",
            "reason-reference": "reference",
            "status": "token",
            "subject": "reference"
        }