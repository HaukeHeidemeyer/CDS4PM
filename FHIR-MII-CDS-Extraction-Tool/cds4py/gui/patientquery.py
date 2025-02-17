from gui.resourcefieldqueryselection import ResourceFieldQuerySelection


class PatientQuerySelectionWidget(ResourceFieldQuerySelection):

    def __init__(self):
        self.resource_name = "Patient"
        super().__init__("Patient")

    def get_parameters(self):
        return {
            "active": "token",
            "address": "string",
            "address-city": "string",
            "address-country": "string",
            "address-postalcode": "string",
            "address-state": "string",
            "address-use": "token",
            "birthdate": "date",
            "death-date": "date",
            "deceased": "token",
            "email": "token",
            "family": "string",
            "gender": "token",
            "general-practitioner": "reference",
            "given": "string",
            "identifier": "token",
            "language": "token",
            "link": "reference",
            "name": "string",
            "organization": "reference",
            "phone": "token",
            "phonetic": "string",
            "telecom": "token"
        }