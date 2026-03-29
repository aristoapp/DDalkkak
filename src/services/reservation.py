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
        cuisine = entities.get("cuisine", "")
        service_type = entities.get("service_type", "")
        party_size = entities.get("party_size", 2)
        date = entities.get("reservation_date", "")
        time = entities.get("reservation_time", "")

        if venue:
            search = venue
        elif cuisine:
            search = f"{cuisine} 맛집"
        elif service_type:
            search = service_type
        else:
            search = "맛집"

        instructions: list[str] = []
        instructions.append(f"캐치테이블 앱을 열고, 검색창에 '{search}'을(를) 검색하세요.")
        instructions.append("예약 가능한 식당을 선택하세요.")

        if date:
            instructions.append(f"날짜를 {date}로 선택하세요.")
        if time:
            instructions.append(f"시간을 {time}으로 선택하세요.")

        instructions.append(f"인원을 {party_size}명으로 설정하세요.")
        instructions.append("예약 양식을 작성하고 결제를 완료하세요.")
        instructions.append("예약 확인 후 '예약내역'에서 즉시 취소하세요.")

        return " ".join(instructions)


class NaverReservationHandler(ServiceHandler):
    def get_package_name(self) -> str:
        return settings.naver_package

    def build_goal(self, intent: ParsedIntent) -> str:
        entities = intent.entities
        venue = entities.get("venue_name", "")
        cuisine = entities.get("cuisine", "")
        service_type = entities.get("service_type", "")
        location = entities.get("location", "")
        party_size = entities.get("party_size", 2)
        date = entities.get("reservation_date", "")
        time = entities.get("reservation_time", "")

        if venue:
            search = venue
        elif cuisine and location:
            search = f"{location} {cuisine}"
        elif cuisine:
            search = f"{cuisine} 맛집"
        elif service_type:
            search = service_type
        else:
            search = "맛집"

        if location and location not in search:
            search = f"{location} {search}"

        instructions: list[str] = []
        instructions.append(f"네이버 앱을 열고, 검색창에 '{search}'을(를) 검색하세요.")
        instructions.append("'예약' 버튼이 있는 장소를 선택하세요.")

        if date:
            instructions.append(f"날짜를 {date}로 선택하세요.")
        if time:
            instructions.append(f"시간을 {time}으로 선택하세요.")

        instructions.append(f"{party_size}명 예약을 완료하세요.")
        instructions.append("예약 확인 후 '예약내역'에서 즉시 취소하세요.")

        return " ".join(instructions)
