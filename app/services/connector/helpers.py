from datetime import datetime

from app.schemas import ClassAvia, ObjectType


def parse_dt(x):
	return datetime.strptime(x, "%d.%m.%Y %H:%M:%S")


def loc_from(x, type_):
	return {
		"type": type_,
		"name": x.get("title") or x.get("code") or "",
	}


def avia_location(airport, city, country, terminal):
	return {
		"airport": loc_from(airport, ObjectType.airport.value),
		"city": loc_from(city, ObjectType.city.value),
		"country": loc_from(country, ObjectType.country.value),
		"terminal": loc_from({"title": terminal or ""}, ObjectType.terminal.value),
	}


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
			return ClassAvia.economy
		case "F":
			return ClassAvia.first
		case "C":
			return ClassAvia.comfort
		case _:
			return ClassAvia.economy
