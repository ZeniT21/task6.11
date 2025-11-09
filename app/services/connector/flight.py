from datetime import timedelta
from decimal import Decimal

from app.data import TEST_AVIA_SERVICE_DETAILS_RESPONSE
from app.schemas import FlightSchema, ObjectType
from app.services.abc_classes import AbstractGetFlightData, AbstractAviaConverter
from app.services.connector.helpers import (direction_data, class_avia, pars_dt, safe_baggage)


class GetFlightData(AbstractGetFlightData):
	def get_flight_data(self):
		return TEST_AVIA_SERVICE_DETAILS_RESPONSE


class AviaConverter(AbstractAviaConverter):

	def transform_flight(self, data) -> FlightSchema:
		flight_data = data["product"]["flight"]

		base_flight = self._build_base_flight(data, flight_data)
		segments = [self._build_segment(seg) for seg in flight_data["segments"]]
		legs = self._build_legs(segments, flight_data)
		baggage_summary = self._build_baggage_summary(segments)

		return FlightSchema(
		    **base_flight,
		    legs=legs,
		    fare_family=flight_data.get("fare_family_flag"),
		    baggage_summary=baggage_summary,
		)

	def _build_base_flight(self, data: dict, flight_data: dict) -> dict:
		return {
		    "id": flight_data["id"],
		    "price": Decimal(flight_data["price"]["RUB"]["amount"]),
		    "is_refundable": flight_data["is_refund"],
		    "is_changeable": any(seg.get("is_change", False) for seg in flight_data["segments"]),
		    "is_travel_policy_compliant": data["product"]["is_travel_policy_compliant"],
		}

	def _build_segment(self, seg: dict) -> dict:
		arrival = seg["arrival"]
		departure = seg["departure"]

		baggage = {
		    "baggage": safe_baggage(seg.get("baggage")),
		    "hand_baggage": safe_baggage(seg.get("cbaggage")),
		}

		return {
			"arrival": direction_data(arrival),
			"arrival_at": pars_dt(arrival["datetime"]),
			"arrival_at_utc": pars_dt(
				arrival["datetime"]) - timedelta(hours=int(arrival["timezone_offset"])),
			"arrival_at_timezone_offset": int(arrival["timezone_offset"]),
			"departure": direction_data(departure),
			"departure_at": pars_dt(departure["datetime"]),
			"departure_at_utc": pars_dt(
				departure["datetime"]) - timedelta(hours=int(departure["timezone_offset"])),
			"departure_at_timezone_offset": int(departure["timezone_offset"]),
			"seats": seg.get("seats") or [],
			"flight_number": seg.get("flight_number") or "",
			"flight_duration": seg.get("duration", {}).get("flight", {}).get("common") or 0,
			"transfer_duration": 0,
			"comment": seg.get("comment") or "",
			"baggage": baggage,
			"flight_class": class_avia(seg.get("class", {}).get("name")),
			"carrier": {
			    "type": ObjectType.carrier.value,
			    "id": str(seg["carrier"]["id"]),
			    "name": seg["carrier"]["title"],
			},
			"fare_code": seg.get("fare_code") or "",
			"aircraft": {
			    "type": ObjectType.airport.value,
			    "id": seg["aircraft"]["code"],
			    "name": seg["aircraft"]["title"],
			},
		}

	def _build_legs(self, segments: list[dict], flight_data: dict) -> list[dict]:
		return [
			{
				"segments": [s],
				"segments_count": flight_data.get("segments_count", len(segments)),
				"route_duration": s["flight_duration"],
			}
			for s in segments
		]

	def _build_baggage_summary(self, segments: list[dict]) -> dict:
		# Получаем все значения baggage и hand_baggage из сегментов
		baggage_list = [s["baggage"]["baggage"] for s in segments]
		hand_baggage_list = [s["baggage"]["hand_baggage"] for s in segments]

		# Находим минимальные значения quantity и weight
		min_baggage = {
			"quantity": min((b["quantity"] for b in baggage_list), default=0),
			"weight": min((b["weight"] for b in baggage_list), default=0),
			"dimensions": min((b["dimensions"] for b in baggage_list if b["dimensions"]), default=""),
		}
		min_hand_baggage = {
			"quantity": min((hb["quantity"] for hb in hand_baggage_list), default=0),
			"weight": min((hb["weight"] for hb in hand_baggage_list), default=0),
			"dimensions": min((hb["dimensions"] for hb in hand_baggage_list if hb["dimensions"]),
			                  default=""),
		}

		return {
			"baggage": min_baggage,
			"hand_baggage": min_hand_baggage,
		}
