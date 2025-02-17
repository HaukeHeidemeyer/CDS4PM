from gui.resourcefieldqueryselection import ResourceFieldQuerySelection


class EncounterQuerySelectionWidget(ResourceFieldQuerySelection):

    def __init__(self):
        super().__init__(resource_name="Encounter")

    def get_parameters(self):
        return {
            "account": "reference",
            "appointment": "reference",
            "based-on": "reference",
            "class": "token",
            "date": "date",
            "diagnosis": "reference",
            "episode-of-care": "reference",
            "identifier": "token",
            "length": "quantity",
            "location": "reference",
            "location-period": "date",
            "part-of": "reference",
            "participant": "reference",
            "participant-type": "token",
            "patient": "reference",
            "practitioner": "reference",
            "reason-code": "token",
            "reason-reference": "reference",
            "service-provider": "reference",
            "special-arrangement": "token",
            "status": "token",
            "subject": "reference",
            "type": "token"
        }

