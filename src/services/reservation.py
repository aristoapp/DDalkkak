from __future__ import annotations

from src.config import settings
from src.intent.schemas import ParsedIntent
from src.services.base import ServiceHandler


class CatchtableHandler(ServiceHandler):
    def get_package_name(self) -> str:
        return settings.catchtable_package

    def build_goal(self, intent: ParsedIntent) -> str:
        entities = intent.entities
        venue = entities.get("venue_name", "")
        service_type = entities.get("service_type", "")
        party_size = entities.get("party_size", 1)
        time = entities.get("reservation_time", "")

        if venue:
            search = venue
        elif service_type:
            search = service_type
        else:
            search = "맛집"

        time_str = f" {time}으로" if time else ""

        return (
            f"캐치테이블 앱을 열고, 검색창에 '{search}'을(를) 검색하세요. "
            f"예약 가능한 식당을 선택하고, {party_size}명{time_str} 예약을 완료하세요. "
            f"예약 확인 후 '예약내역'에서 즉시 취소하세요."
        )


class NaverReservationHandler(ServiceHandler):
    def get_package_name(self) -> str:
        return settings.naver_package

    def build_goal(self, intent: ParsedIntent) -> str:
        entities = intent.entities
        venue = entities.get("venue_name", "")
        service_type = entities.get("service_type", "")
        location = entities.get("location", "")
        party_size = entities.get("party_size", 1)

        search = venue or service_type or "맛집"
        loc_str = f" {location}" if location else ""

        return (
            f"네이버 앱을 열고, 검색창에 '{search}{loc_str}'을(를) 검색하세요. "
            f"'예약' 버튼이 있는 장소를 선택하고, {party_size}명 예약을 완료하세요. "
            f"예약 확인 후 '예약내역'에서 즉시 취소하세요."
        )
