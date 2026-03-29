from __future__ import annotations

from src.config import settings
from src.intent.schemas import ParsedIntent
from src.services.base import ServiceHandler


class KakaoGiftHandler(ServiceHandler):
    def get_package_name(self) -> str:
        return settings.kakao_package

    def build_goal(self, intent: ParsedIntent) -> str:
        entities = intent.entities
        recipient = entities.get("recipient", "받는 사람")
        item_type = entities.get("item_type", "")
        budget = entities.get("budget", "")
        occasion = entities.get("occasion", "")

        item_str = item_type or "인기 선물"
        budget_str = f" {budget} 이내로" if budget else ""
        occasion_str = f" ({occasion})" if occasion else ""

        return (
            f"카카오톡 앱을 열고, 하단 '더보기' 탭 → '선물하기'로 이동하세요. "
            f"'{item_str}'을(를) 검색하여{budget_str} 적절한 상품을 선택하세요. "
            f"'{recipient}'{occasion_str}에게 선물하기를 완료하세요. "
            f"전송 후 상대방이 확인하기 전에 '선물내역'에서 즉시 취소하세요."
        )
