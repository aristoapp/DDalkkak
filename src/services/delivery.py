from __future__ import annotations

from src.config import settings
from src.intent.schemas import ParsedIntent
from src.services.base import ServiceHandler


class BaeminHandler(ServiceHandler):
    def get_package_name(self) -> str:
        return settings.baemin_package

    def build_goal(self, intent: ParsedIntent) -> str:
        entities = intent.entities
        cuisine = entities.get("cuisine", "")
        restaurant = entities.get("restaurant", "")

        if restaurant:
            return (
                f"배달의민족 앱을 열고, 검색창에 '{restaurant}'을(를) 검색하세요. "
                f"메뉴를 선택하고 장바구니에 담은 뒤 결제를 완료하세요. "
                f"주문 완료 후 '주문내역'에서 조리 시작 전에 즉시 주문을 취소하세요."
            )

        return (
            f"배달의민족 앱을 열고, {f'{cuisine} 카테고리에서' if cuisine else '추천 메뉴에서'} "
            f"평점이 높은 음식점을 선택하세요. "
            f"메뉴를 선택하고 장바구니에 담은 뒤 결제를 완료하세요. "
            f"주문 완료 후 '주문내역'에서 조리 시작 전에 즉시 주문을 취소하세요."
        )


class CoupangEatsHandler(ServiceHandler):
    def get_package_name(self) -> str:
        return settings.coupang_eats_package

    def build_goal(self, intent: ParsedIntent) -> str:
        entities = intent.entities
        cuisine = entities.get("cuisine", "")
        restaurant = entities.get("restaurant", "")

        if restaurant:
            return (
                f"쿠팡이츠 앱을 열고, 검색창에 '{restaurant}'을(를) 검색하세요. "
                f"메뉴를 선택하고 장바구니에 담은 뒤 결제를 완료하세요. "
                f"주문 완료 후 '주문내역'에서 조리 시작 전에 즉시 주문을 취소하세요."
            )

        return (
            f"쿠팡이츠 앱을 열고, {f'{cuisine} 카테고리에서' if cuisine else '추천 메뉴에서'} "
            f"평점이 높은 음식점을 선택하세요. "
            f"메뉴를 선택하고 장바구니에 담은 뒤 결제를 완료하세요. "
            f"주문 완료 후 '주문내역'에서 조리 시작 전에 즉시 주문을 취소하세요."
        )
