from datetime import timedelta
from decimal import Decimal

from app.data import TEST_AVIA_SERVICE_DETAILS_RESPONSE
from app.schemas import FlightSchema
from app.services.abc_classes import AbstractFlight
from app.services.connector.helpers import (avia_location, class_avia,
                                            parse_dt, safe_baggage)


class Flight(AbstractFlight):

	def get_flight(self):
		return TEST_AVIA_SERVICE_DETAILS_RESPONSE

	def transform_flight(self, data) -> FlightSchema:
		flight_data = data["product"]["flight"]

		base_flight = {
			"id": flight_data["id"],
			"price": Decimal(flight_data["price"]["RUB"]["amount"]),
			"is_refundable": flight_data["is_refund"],
			"is_changeable": any(seg.get("is_change", False) for seg in flight_data["segments"]),
			"is_travel_policy_compliant": data["product"]["is_travel_policy_compliant"],
		}

		segments = []
		for seg in flight_data["segments"]:
			arrival = seg["arrival"]
			departure = seg["departure"]

			baggage = {
				"baggage": safe_baggage(seg.get("baggage")),
				"hand_baggage": safe_baggage(seg.get("cbaggage")),
			}

			segment = {
				"arrival": avia_location(arrival["airport"], arrival["city"], arrival["country"],
				                         arrival.get("terminal")),
				"arrival_at": parse_dt(arrival["datetime"]),
				"arrival_at_utc": parse_dt(arrival["datetime"])-timedelta(hours=int(arrival["timezone_offset"])),
				"arrival_at_timezone_offset": int(arrival["timezone_offset"]),
				"departure": avia_location(departure["airport"], departure["city"],
				                           departure["country"],
				                           departure.get("terminal")),
				"departure_at": parse_dt(departure["datetime"]),
				"departure_at_utc": parse_dt(departure["datetime"]) - timedelta(
					hours=int(departure["timezone_offset"])),
				"departure_at_timezone_offset": int(departure["timezone_offset"]),
				"seats": seg.get("seats") or [],
				"flight_number": seg.get("flight_number") or "",
				"flight_duration": seg.get("duration", {}).get("flight", {}).get("common") or 0,
				"transfer_duration": 0,
				"comment": seg.get("comment") or "",
				"baggage": baggage,
				"flight_class": class_avia(seg.get("class", {}).get("name")),
				"carrier": {
					"type": "carrier",
					"id": str(seg["carrier"]["id"]),
					"name": seg["carrier"]["title"],
				},
				"fare_code": seg.get("fare_code") or "",
				"aircraft": {
					"type": "aircraft",
					"id": seg["aircraft"]["code"],
					"name": seg["aircraft"]["title"],
				},
			}

			segments.append(segment)

		legs = [
			{
				"segments": [s],
				"segments_count": flight_data.get("segments_count", len(segments)),
				"route_duration": s["flight_duration"],
			}
			for s in segments
		]

		min_baggage = {
			"quantity": min((s["baggage"]["baggage"]["quantity"] for s in segments), default=0),
			"weight": min((s["baggage"]["baggage"]["weight"] for s in segments), default=0),
			"dimensions": "",
		}
		min_hand_baggage = {
			"quantity": min((s["baggage"]["hand_baggage"]["quantity"] for s in segments), default=0),
			"weight": min((s["baggage"]["hand_baggage"]["weight"] for s in segments), default=0),
			"dimensions": "",
		}

		baggage_summary = {
			"baggage": min_baggage,
			"hand_baggage": min_hand_baggage,
		}

		flight_model = FlightSchema(
			**base_flight,
			legs=legs,
			fare_family=flight_data.get("fare_family_flag"),
			baggage_summary=baggage_summary,
		)

		return flight_model
