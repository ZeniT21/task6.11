from abc import ABC, abstractmethod


class AbstractFlight(ABC):

    @abstractmethod
    def get_flight(self, *args, **kwargs):
        pass

    @abstractmethod
    def transform_flight(self, *args, **kwargs):
        pass
