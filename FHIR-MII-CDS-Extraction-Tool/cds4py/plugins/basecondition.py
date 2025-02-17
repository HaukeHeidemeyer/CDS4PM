from abc import ABC, abstractmethod

class BaseCondition(ABC):
    def __init__(self):
        self.name = None
        self.restricted_to = []

    @abstractmethod
    def evaluate(self, value, column_values):
        pass

    def is_applicable_to(self, resource_type):
        return not self.restricted_to or resource_type in self.restricted_to
