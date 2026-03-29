"""Demo scenario script — run with: uv run python scripts/demo.py"""

from __future__ import annotations

import asyncio

from src.intent.parser import IntentParser
from src.router.router import ServiceRouter

DEMO_INPUTS = [
    "샴푸 다 떨어졌다. 주문해줘",
    "오늘 저녁 혼자 먹을 거 추천해서 주문해줘",
    "내일 아침 7시에 공항 가는 택시 잡아줘",
    "이번 주말 제주도 숙소 예약해줘",
    "근처 맛집 예약해줘",
    "부모님 집으로 과일 선물 보내줘",
]


async def main() -> None:
    parser = IntentParser()
    router = ServiceRouter()

    print("=" * 60)
    print("DDalkkak Demo — Intent Parsing + Routing")
    print("=" * 60)

    for user_input in DEMO_INPUTS:
        print(f"\n💬 Input: {user_input}")
        intent = await parser.parse(user_input)
        app_key, package_name, display_name = router.route(intent)
        print(f"   Category: {intent.category.value}")
        print(f"   Action: {intent.action.value}")
        print(f"   App: {display_name} ({package_name})")
        print(f"   Confidence: {intent.confidence}")
        print(f"   Goal: {intent.minitap_goal[:80]}...")


if __name__ == "__main__":
    asyncio.run(main())
