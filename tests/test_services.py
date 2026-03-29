from __future__ import annotations

from src.intent.schemas import ParsedIntent, ServiceAction, ServiceCategory
from src.services.delivery import BaeminHandler, CoupangEatsHandler
from src.services.gift import KakaoGiftHandler
from src.services.mobility import KakaoTHandler
from src.services.reservation import CatchtableHandler, NaverReservationHandler
from src.services.shopping import CoupangHandler, NaverShoppingHandler
from src.services.travel import YanoljaHandler


def _make_intent(category: ServiceCategory, entities: dict | None = None) -> ParsedIntent:
    return ParsedIntent(
        category=category,
        action=ServiceAction.ORDER,
        entities=entities or {},
        minitap_goal="test goal",
    )


class TestShoppingHandlers:
    def test_coupang_goal(self) -> None:
        intent = _make_intent(ServiceCategory.SHOPPING, {"product": "샴푸", "quantity": 2})
        handler = CoupangHandler(agent=None)
        goal = handler.build_goal(intent)
        assert "샴푸" in goal
        assert "취소" in goal

    def test_coupang_reorder(self) -> None:
        intent = _make_intent(ServiceCategory.SHOPPING, {"product": "샴푸", "use_previous_order": True})
        handler = CoupangHandler(agent=None)
        goal = handler.build_goal(intent)
        assert "다시 주문하기" in goal
        assert "취소" in goal

    def test_naver_shopping_goal(self) -> None:
        intent = _make_intent(ServiceCategory.SHOPPING, {"product": "이어폰"})
        handler = NaverShoppingHandler(agent=None)
        goal = handler.build_goal(intent)
        assert "이어폰" in goal
        assert "취소" in goal


class TestDeliveryHandlers:
    def test_baemin_with_restaurant(self) -> None:
        intent = _make_intent(ServiceCategory.DELIVERY, {"restaurant": "맘스터치"})
        handler = BaeminHandler(agent=None)
        goal = handler.build_goal(intent)
        assert "맘스터치" in goal
        assert "취소" in goal

    def test_baemin_with_cuisine(self) -> None:
        intent = _make_intent(ServiceCategory.DELIVERY, {"cuisine": "치킨"})
        handler = BaeminHandler(agent=None)
        goal = handler.build_goal(intent)
        assert "치킨" in goal
        assert "취소" in goal

    def test_coupang_eats_goal(self) -> None:
        intent = _make_intent(ServiceCategory.DELIVERY, {"cuisine": "피자"})
        handler = CoupangEatsHandler(agent=None)
        goal = handler.build_goal(intent)
        assert "쿠팡이츠" in goal
        assert "취소" in goal


class TestMobilityHandler:
    def test_kakaot_with_time(self) -> None:
        intent = _make_intent(ServiceCategory.MOBILITY, {"destination": "강남역", "pickup_time": "내일 오전 7시"})
        handler = KakaoTHandler(agent=None)
        goal = handler.build_goal(intent)
        assert "강남역" in goal
        assert "내일 오전 7시" in goal
        assert "취소" in goal

    def test_kakaot_without_time(self) -> None:
        intent = _make_intent(ServiceCategory.MOBILITY, {"destination": "공항"})
        handler = KakaoTHandler(agent=None)
        goal = handler.build_goal(intent)
        assert "공항" in goal
        assert "취소" in goal


class TestTravelHandler:
    def test_yanolja_goal(self) -> None:
        intent = _make_intent(ServiceCategory.TRAVEL, {"destination": "제주도", "num_guests": 2})
        handler = YanoljaHandler(agent=None)
        goal = handler.build_goal(intent)
        assert "제주도" in goal
        assert "무료 취소" in goal


class TestReservationHandlers:
    def test_catchtable_with_venue(self) -> None:
        intent = _make_intent(ServiceCategory.RESERVATION, {"venue_name": "스시미소", "party_size": 4})
        handler = CatchtableHandler(agent=None)
        goal = handler.build_goal(intent)
        assert "스시미소" in goal
        assert "취소" in goal

    def test_catchtable_with_cuisine_and_datetime(self) -> None:
        intent = _make_intent(
            ServiceCategory.RESERVATION,
            {"cuisine": "양식", "party_size": 2, "reservation_date": "4월 4일", "reservation_time": "오후 6시"},
        )
        handler = CatchtableHandler(agent=None)
        goal = handler.build_goal(intent)
        assert "양식 맛집" in goal
        assert "4월 4일" in goal
        assert "오후 6시" in goal
        assert "2명" in goal
        assert "취소" in goal

    def test_naver_reservation_goal(self) -> None:
        intent = _make_intent(ServiceCategory.RESERVATION, {"service_type": "맛집", "location": "강남"})
        handler = NaverReservationHandler(agent=None)
        goal = handler.build_goal(intent)
        assert "맛집" in goal
        assert "강남" in goal
        assert "취소" in goal

    def test_naver_reservation_with_cuisine(self) -> None:
        intent = _make_intent(
            ServiceCategory.RESERVATION,
            {"cuisine": "일식", "location": "홍대", "party_size": 3, "reservation_date": "금요일"},
        )
        handler = NaverReservationHandler(agent=None)
        goal = handler.build_goal(intent)
        assert "일식" in goal
        assert "홍대" in goal
        assert "3명" in goal
        assert "금요일" in goal


class TestGiftHandler:
    def test_kakao_gift_goal(self) -> None:
        intent = _make_intent(ServiceCategory.GIFT, {"recipient": "엄마", "item_type": "과일", "occasion": "생일"})
        handler = KakaoGiftHandler(agent=None)
        goal = handler.build_goal(intent)
        assert "엄마" in goal
        assert "과일" in goal
        assert "취소" in goal
