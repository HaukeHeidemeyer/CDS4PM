from gui.resourcefieldqueryselection import ResourceFieldQuerySelection


class ConditionQuerySelectionWidget(ResourceFieldQuerySelection):

    def __init__(self):
        self.resource_name = "Condition"
        super().__init__(resource_name="Condition")

    def get_parameters(self):
        return {
            "abatement-age": "quantity",
            "abatement-date": "date",
            "abatement-string": "string",
            "asserter": "reference",
            "body-site": "token",
            "category": "token",
            "clinical-status": "token",
            "code": "token",
            "encounter": "reference",
            "evidence": "token",
            "evidence-detail": "reference",
            "identifier": "token",
            "onset-age": "quantity",
            "onset-date": "date",
            "onset-info": "string",
            "patient": "reference",
            "recorded-date": "date",
            "severity": "token",
            "stage": "token",
            "subject": "reference",
            "verification-status": "token"
        }

