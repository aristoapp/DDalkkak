from __future__ import annotations

import pytest

from src.intent.schemas import ParsedIntent, ServiceAction, ServiceCategory
from src.router.router import ServiceRouter


@pytest.fixture
def router() -> ServiceRouter:
    return ServiceRouter()


def _make_intent(category: ServiceCategory, **kwargs) -> ParsedIntent:
    return ParsedIntent(
        category=category,
        action=ServiceAction.ORDER,
        entities={},
        minitap_goal="test",
        **kwargs,
    )


@pytest.mark.parametrize(
    "category,expected_key",
    [
        (ServiceCategory.SHOPPING, "coupang"),
        (ServiceCategory.DELIVERY, "baemin"),
        (ServiceCategory.MOBILITY, "kakaot"),
        (ServiceCategory.TRAVEL, "yanolja"),
        (ServiceCategory.RESERVATION, "catchtable"),
        (ServiceCategory.GIFT, "kakao_gift"),
    ],
)
def test_default_routing(router: ServiceRouter, category: ServiceCategory, expected_key: str) -> None:
    intent = _make_intent(category)
    app_key, package_name, name = router.route(intent)
    assert app_key == expected_key
    assert package_name
    assert name


def test_app_preference_routing(router: ServiceRouter) -> None:
    intent = _make_intent(ServiceCategory.SHOPPING, app_preference="naver_shopping")
    app_key, _, name = router.route(intent)
    assert app_key == "naver_shopping"
    assert name == "네이버쇼핑"


def test_app_preference_delivery(router: ServiceRouter) -> None:
    intent = _make_intent(ServiceCategory.DELIVERY, app_preference="coupang_eats")
    app_key, _, name = router.route(intent)
    assert app_key == "coupang_eats"
    assert name == "쿠팡이츠"
