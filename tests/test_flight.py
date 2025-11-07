from decimal import Decimal
from unittest.mock import patch

import pytest
from data.data import TEST_AVIA_SERVICE_DETAILS_RESPONSE as test_resp

from app.services.connector.flight import Flight


@pytest.fixture
def flight_instance():
    return Flight()


@patch.object(Flight, 'get_flight')
def test_transform_flight(mock_get_flight, flight_instance):
    mock_get_flight.return_value = test_resp

    raw_data = flight_instance.get_flight()
    flight_model = flight_instance.transform_flight(raw_data)

    assert flight_model.id == test_resp["product"]["flight"]["id"]
    assert flight_model.price == Decimal(test_resp["product"]["flight"]["price"]["RUB"]["amount"])
    assert flight_model.is_refundable == test_resp["product"]["flight"]["is_refund"]

    assert len(flight_model.legs) == len(test_resp["product"]["flight"]["segments"])

    assert flight_model.fare_family == test_resp["product"]["flight"].get("fare_family_flag")


def test_baggage_summary(flight_instance):
    raw_data = test_resp
    flight_model = flight_instance.transform_flight(raw_data)

    segments = flight_model.legs

    min_baggage_weight = min(
        seg.segments[0].baggage.baggage.weight for seg in segments
    )
    min_hand_baggage_weight = min(
        seg.segments[0].baggage.hand_baggage.weight for seg in segments
    )

    min_baggage_quantity = min(
        seg.segments[0].baggage.baggage.quantity for seg in segments
    )
    min_hand_baggage_quantity = min(
        seg.segments[0].baggage.hand_baggage.quantity for seg in segments
    )

    assert flight_model.baggage_summary.baggage.weight == min_baggage_weight
    assert flight_model.baggage_summary.hand_baggage.weight == min_hand_baggage_weight
    assert flight_model.baggage_summary.baggage.quantity == min_baggage_quantity
    assert flight_model.baggage_summary.hand_baggage.quantity == min_hand_baggage_quantity
