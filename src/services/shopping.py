from __future__ import annotations

from src.config import settings
from src.intent.schemas import ParsedIntent
from src.services.base import ServiceHandler


class CoupangHandler(ServiceHandler):
    def get_package_name(self) -> str:
        return settings.coupang_package

    def build_goal(self, intent: ParsedIntent) -> str:
        entities = intent.entities
        product = entities.get("product", "상품")

        if entities.get("use_previous_order"):
            return (
                f"쿠팡 앱을 열고, '마이쿠팡' → '주문목록'에서 "
                f"가장 최근에 주문한 {product}을(를) 찾아서 '다시 주문하기'를 눌러주세요. "
                f"결제를 완료하세요. 주문 완료 후 '주문내역'에서 해당 주문을 즉시 취소하세요."
            )

        brand = entities.get("brand", "")
        quantity = entities.get("quantity", 1)
        return (
            f"쿠팡 앱을 열고, 검색창에 '{brand} {product}'을(를) 검색하세요. "
            f"로켓배송 상품 중 평점이 높은 것을 선택하고, "
            f"수량 {quantity}개로 설정한 뒤 결제를 완료하세요. "
            f"주문 완료 후 '주문내역'에서 해당 주문을 즉시 취소하세요."
        )


class NaverShoppingHandler(ServiceHandler):
    def get_package_name(self) -> str:
        return settings.naver_package

    def build_goal(self, intent: ParsedIntent) -> str:
        entities = intent.entities
        product = entities.get("product", "상품")
        return (
            f"네이버 앱을 열고, 검색창에 '{product}'을(를) 검색하세요. "
            f"'쇼핑' 탭으로 이동하여 가격이 적절한 상품을 선택하고, "
            f"결제를 완료하세요. 주문 완료 후 '주문내역'에서 즉시 취소하세요."
        )
