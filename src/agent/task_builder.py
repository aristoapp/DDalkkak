from __future__ import annotations

from src.intent.schemas import ParsedIntent, ServiceCategory

SAFETY_SUFFIXES = {
    ServiceCategory.SHOPPING: "결제를 완료하세요. 주문 완료 후 '주문내역'에서 해당 주문을 즉시 취소하세요.",
    ServiceCategory.DELIVERY: "결제를 완료하세요. 주문 완료 후 '주문내역'에서 조리 시작 전에 즉시 주문을 취소하세요.",
    ServiceCategory.MOBILITY: "호출을 완료하세요. 기사 배정 전이든 후든 즉시 '호출 취소'를 눌러 취소하세요.",
    ServiceCategory.TRAVEL: (
        "무료 취소가 가능한 상품만 선택하세요. 결제를 완료한 후, '예약내역'에서 즉시 무료 취소하세요."
    ),
    ServiceCategory.RESERVATION: "예약을 완료하세요. 예약 확인 후 '예약내역'에서 즉시 취소하세요.",
    ServiceCategory.GIFT: "선물하기를 완료하세요. 전송 후 상대방이 확인하기 전에 '선물내역'에서 즉시 취소하세요.",
}


class TaskGoalBuilder:
    @staticmethod
    def build_goal(intent: ParsedIntent) -> str:
        suffix = SAFETY_SUFFIXES.get(intent.category, "")
        return f"{intent.minitap_goal} {suffix}".strip()
