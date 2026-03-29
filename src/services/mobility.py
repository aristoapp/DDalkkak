from __future__ import annotations

from src.config import settings
from src.intent.schemas import ParsedIntent
from src.services.base import ServiceHandler


class KakaoTHandler(ServiceHandler):
    def get_package_name(self) -> str:
        return settings.kakaot_package

    def build_goal(self, intent: ParsedIntent) -> str:
        entities = intent.entities
        dest = entities.get("destination", "목적지")
        pickup_time = entities.get("pickup_time", "")
        time_str = f"{pickup_time}에 " if pickup_time else ""
        return (
            f"카카오T 앱을 열고, {time_str}{dest}까지 택시를 호출해주세요. "
            f"예약이 완료되면, 바로 해당 예약을 취소해주세요."
        )
