from .resourcefieldqueryselection import ResourceFieldQuerySelection


class ObservationQuerySelectionWidget(ResourceFieldQuerySelection):

    def __init__(self):
        self.resource_name = "Observation"
        super().__init__("Observation")

    def get_parameters(self):
        return {
            "based-on": "reference",
            "category": "token",
            "code": "token",
            "code-value-concept": "composite",
            "code-value-date": "composite",
            "code-value-quantity": "composite",
            "code-value-string": "composite",
            "combo-code": "token",
            "combo-code-value-concept": "composite",
            "combo-code-value-quantity": "composite",
            "combo-data-absent-reason": "token",
            "combo-value-concept": "token",
            "combo-value-quantity": "quantity",
            "component-code": "token",
            "component-code-value-concept": "composite",
            "component-code-value-quantity": "composite",
            "component-data-absent-reason": "token",
            "component-value-concept": "token",
            "component-value-quantity": "quantity",
            "data-absent-reason": "token",
            "date": "date",
            "derived-from": "reference",
            "device": "reference",
            "encounter": "reference",
            "focus": "reference",
            "has-member": "reference",
            "identifier": "token",
            "method": "token",
            "part-of": "reference",
            "patient": "reference",
            "performer": "reference",
            "specimen": "reference",
            "status": "token",
            "subject": "reference",
            "value-concept": "token",
            "value-date": "date",
            "value-quantity": "quantity",
            "value-string": "string"
        }