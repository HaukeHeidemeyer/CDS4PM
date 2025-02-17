from .resourcefieldqueryselection import ResourceFieldQuerySelection

class PractitionerRoleQuerySelectionWidget(ResourceFieldQuerySelection):

    def __init__(self):
        self.resource_name = "PractitionerRole"
        super().__init__(resource_name="PractitionerRole")

    def get_parameters(self):
        return {
            "active": "token",  # Whether this practitioner role record is in active use
            "date": "date",  # The period during which the practitioner is authorized to perform in these role(s)
            "email": "token",  # A value in an email contact
            "endpoint": "reference",  # Technical endpoints providing access to services operated for the practitioner with this role
            "identifier": "token",  # A practitioner's Identifier
            "location": "reference",  # One of the locations at which this practitioner provides care
            "organization": "reference",  # The identity of the organization the practitioner represents / acts on behalf of
            "phone": "token",  # A value in a phone contact
            "practitioner": "reference",  # Practitioner that is able to provide the defined services for the organization
            "role": "token",  # The practitioner can perform this role for the organization
            "service": "reference",  # The list of healthcare services that this worker provides for this role's Organization/Location(s)
            "specialty": "token",  # The practitioner has this specialty at an organization
            "telecom": "token"  # The value in any kind of contact
        }
