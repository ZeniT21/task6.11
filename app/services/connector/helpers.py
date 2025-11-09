from datetime import datetime

from app.schemas import ClassAvia, ObjectType


def pars_dt(x):
	return datetime.strptime(x, "%d.%m.%Y %H:%M:%S")


def safe_baggage(bag: dict) -> dict:
	bag = bag or {}
	return {
		"quantity": bag.get("piece") or 0,
		"weight": bag.get("weight") or 0,
		"dimensions": bag.get("dimensions") or "",
	}


def class_avia(class_type: str) -> ClassAvia:
	match class_type:
		case "B":
			return ClassAvia.economy.value
		case "F":
			return ClassAvia.first.value
		case "C":
			return ClassAvia.comfort.value
		case _:
			return ClassAvia.economy.value


def direction_data(segment_direction):
	return {
		"airport": {"type": ObjectType.airport, "name": segment_direction["airport"]["title"]},
		"country": {"type": ObjectType.country, "name": segment_direction["country"]["title"]},
		"city": {"type": ObjectType.city, "name": segment_direction["city"]["title"]},
		"terminal": {"type": ObjectType.terminal, "name": segment_direction["terminal"]},
	}
