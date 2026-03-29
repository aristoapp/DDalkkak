from __future__ import annotations

from enum import StrEnum
from importlib import import_module
from typing import Any

_pydantic = import_module("pydantic")
BaseModel = _pydantic.BaseModel
Field = _pydantic.Field


class ServiceCategory(StrEnum):
    SHOPPING = "shopping"
    DELIVERY = "delivery"
    MOBILITY = "mobility"
    TRAVEL = "travel"
    RESERVATION = "reservation"
    GIFT = "gift"


class ServiceAction(StrEnum):
    ORDER = "order"
    SEARCH = "search"
    BOOK = "book"
    RESERVE = "reserve"
    CANCEL = "cancel"
    COMPARE = "compare"
    RECOMMEND = "recommend"


class ShoppingEntities(BaseModel):
    product: str
    brand: str | None = None
    quantity: int = 1
    price_range: str | None = None
    use_previous_order: bool = False


class DeliveryEntities(BaseModel):
    cuisine: str | None = None
    restaurant: str | None = None
    price_range: str | None = None
    solo_or_group: str | None = None
    time: str | None = None


class MobilityEntities(BaseModel):
    destination: str
    pickup_time: str | None = None
    vehicle_type: str | None = None


class TravelEntities(BaseModel):
    destination: str
    dates: str | None = None
    accommodation_type: str | None = None
    budget: str | None = None
    num_guests: int = 1


class ReservationEntities(BaseModel):
    cuisine: str | None = None
    service_type: str | None = None
    venue_name: str | None = None
    location: str | None = None
    party_size: int = 1
    reservation_date: str | None = None
    reservation_time: str | None = None


class GiftEntities(BaseModel):
    recipient: str
    occasion: str | None = None
    item_type: str | None = None
    budget: str | None = None
    delivery_address: str | None = None


class ParsedIntent(BaseModel):
    category: ServiceCategory
    action: ServiceAction
    entities: dict[str, Any] = Field(default_factory=dict)
    app_preference: str | None = None
    app_target: str | None = None
    minitap_goal: str
    needs_clarification: bool = False
    clarification_question: str | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
