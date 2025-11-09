from abc import ABC, abstractmethod

from app.schemas import FlightSchema


class AbstractGetFlightData(ABC):

    @abstractmethod
    def get_flight_data(self, *args, **kwargs):
        pass


class AbstractAviaConverter(ABC):
    @abstractmethod
    def transform_flight(self, *args, **kwargs) -> FlightSchema:
        pass
