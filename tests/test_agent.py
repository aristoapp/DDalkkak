from __future__ import annotations

import pytest

from src.agent.task_builder import TaskGoalBuilder
from src.intent.schemas import ParsedIntent, ServiceAction, ServiceCategory


def _make_intent(category: ServiceCategory, goal: str = "test") -> ParsedIntent:
    return ParsedIntent(
        category=category,
        action=ServiceAction.ORDER,
        entities={},
        minitap_goal=goal,
    )


class TestTaskGoalBuilder:
    @pytest.mark.parametrize(
        "category,expected_keyword",
        [
            (ServiceCategory.SHOPPING, "즉시 취소"),
            (ServiceCategory.DELIVERY, "즉시 주문을 취소"),
            (ServiceCategory.MOBILITY, "호출 취소"),
            (ServiceCategory.TRAVEL, "무료 취소"),
            (ServiceCategory.RESERVATION, "즉시 취소"),
            (ServiceCategory.GIFT, "즉시 취소"),
        ],
    )
    def test_safety_suffix_per_category(self, category: ServiceCategory, expected_keyword: str) -> None:
        intent = _make_intent(category, goal="기본 작업 수행")
        result = TaskGoalBuilder.build_goal(intent)
        assert expected_keyword in result
        assert "기본 작업 수행" in result

    def test_goal_preserves_original(self) -> None:
        intent = _make_intent(ServiceCategory.SHOPPING, goal="쿠팡에서 샴푸 주문")
        result = TaskGoalBuilder.build_goal(intent)
        assert result.startswith("쿠팡에서 샴푸 주문")
