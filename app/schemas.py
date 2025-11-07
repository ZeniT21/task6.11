from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class BaseFlight(BaseModel):
    id: str | None = Field(..., description='ID рейса')
    price: Decimal = Field(..., description='Стоимость билета')
    is_refundable: bool = Field(
        None,
        description='Признак возможности возврата',
    )
    is_changeable: bool = Field(
        None,
        description='Признак возможности обмена',
    )
    is_travel_policy_compliant: bool = Field(..., description='Флаг соответствия travel policy')


class TransportBaggage(BaseModel):
    quantity: int = None
    weight: int = None
    dimensions: str = None


class FlightBaggage(BaseModel):
    baggage: TransportBaggage = None
    hand_baggage: TransportBaggage = None

    def __bool__(self):
        return self.baggage is not None or self.hand_baggage is not None


class ObjectType(str, Enum):
    city = 'city'
    country = 'country'
    airport = 'airport'
    carrier = 'carrier'
    aircraft = 'aircraft'
    terminal = 'terminal'
    train_station = 'train_station'


class BaseInfo(BaseModel):
    """Сущность, имеющая тип, ID и название """
    type: ObjectType = Field(..., description='Тип сущности')
    id: str = Field(..., description='ID сущности')
    name: str = Field(..., description='Название сущности')


class Loc(BaseModel):
    """Объект месторасположения """
    type: ObjectType = Field(..., description='Тип расположения')
    name: str = Field(..., description='Название расположения')


class BaseLocation(BaseModel):
    """Базовый класс расположения """
    country: Loc = Field(None, description='Страна')
    city: Loc = Field(None, description='Город')


class AviaLocation(BaseLocation):
    """Расположение авиа """
    airport: Loc = Field(None, description='Аэропорт')
    terminal: Loc = Field(None, description='Терминал')


class ClassAvia(str, Enum):
    economy = 'Econom'
    business = 'Business'
    first = 'First'
    comfort = 'Comfort'


class ProviderSegment(BaseModel):
    """Сегмент перелёта """
    arrival: AviaLocation = Field(..., description='Локация прибытия')
    arrival_at: datetime = Field(..., description='Дата и время прибытия')
    arrival_at_utc: datetime = Field(..., description='Дата и время прибытия в utc')
    arrival_at_timezone_offset: int = Field(..., description='Часовой пояс прибытия')
    departure: AviaLocation = Field(..., description='Локация отправления')
    departure_at: datetime = Field(..., description='Дата и время отправления')
    departure_at_utc: datetime = Field(..., description='Дата и время отправления в utc')
    departure_at_timezone_offset: int = Field(..., description='Часовой пояс отправления')
    seats: int | None = Field(..., description='Количество мест')
    flight_number: str = Field(..., description='Номер рейса')
    flight_duration: int = Field(None, description='Время перелёта в минутах')
    transfer_duration: int = Field(None, description='Время пересадки в минутах')
    comment: str = Field(None, description='Комментарий')
    baggage: FlightBaggage = None
    flight_class: ClassAvia = Field(..., description='Класс обслуживания')
    carrier: BaseInfo = Field(..., description='Авиакомпания')
    fare_code: str | None = Field(..., description='Вид тарифа')
    aircraft: BaseInfo = Field(None, description='Самолёт')


class ProviderLeg(BaseModel):
    """Перелёт """
    segments: list[ProviderSegment] = Field(
        ...,
        description=(
            'Список сегментов билета, '
            'В случае с АК, может содержать только 1 сегмент, '
            'так как нет информации о каждой пересадке'
        ),
    )
    segments_count: int = Field(
        ...,
        description='Количество пересадок. Необходимо, так как у АК нет информации о пересадках',
    )
    route_duration: int = Field(..., description='Время в пути в минутах')


class FlightSchema(BaseFlight):
    """Рейс """

    legs: list[ProviderLeg] = Field(
        None,
        description=(
            'Список из одного рейса (в случае билета только "туда") '
            'или из двух (Если билет "Туда-обратно")'
        ),
    )
    fare_family: bool = Field(
        False,
        description='Признак наличия семейства тарифов',
    )
    baggage_summary: FlightBaggage | None = Field(
        None,
        description='Суммарная информация по багажу в fare_family',
    )
