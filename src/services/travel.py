from __future__ import annotations

from src.config import settings
from src.intent.schemas import ParsedIntent
from src.services.base import ServiceHandler


class YanoljaHandler(ServiceHandler):
    def get_bundle_id(self) -> str:
        return settings.yanolja_bundle_id

    def build_goal(self, intent: ParsedIntent) -> str:
        entities = intent.entities
        dest = entities.get("destination", "")
        dates = entities.get("dates", "")
        accom = entities.get("accommodation_type", "")
        num_guests = entities.get("num_guests", 1)

        search_term = dest or "숙소"
        date_str = f" {dates}" if dates else ""
        accom_str = f" {accom}" if accom else ""

        return (
            f"야놀자 앱을 열고, 검색창에 '{search_term}{accom_str}'을(를) 검색하세요.{date_str} "
            f"인원 {num_guests}명으로 설정하고, 무료 취소가 가능한 상품만 선택하세요. "
            f"결제를 완료한 후, '예약내역'에서 즉시 무료 취소하세요."
        )
