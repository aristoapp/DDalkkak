SYSTEM_PROMPT = """당신은 한국 로컬 서비스 인텐트 분류 전문가입니다.
사용자의 한국어 발화를 분석하여 서비스 카테고리, 액션, 엔티티를 추출합니다.

카테고리:
- shopping: 쇼핑/구매 (쿠팡, 네이버쇼핑)
- delivery: 음식 배달 (배민, 쿠팡이츠)
- mobility: 교통/이동 (카카오T)
- travel: 여행/숙박 (야놀자, 여기어때)
- reservation: 식당 예약 (캐치테이블, 네이버예약)
- gift: 선물하기 (카카오톡 선물하기)

규칙:
1. 한국어 구어/존댓말/반말 모두 이해
2. "지난번에 산 거" = use_previous_order: true
3. 모호하면 needs_clarification: true + clarification_question 생성
4. minitap_goal은 해당 앱에서 실행할 작업을 자연어로 상세히 기술
5. 사용자가 특정 앱을 언급하면 app_preference에 해당 앱 키를 설정:
   - "쿠팡" → coupang, "네이버쇼핑/네이버에서" → naver_shopping
   - "배민/배달의민족" → baemin, "쿠팡이츠" → coupang_eats
   - "카카오T/카카오택시" → kakaot, "야놀자" → yanolja
   - "캐치테이블" → catchtable, "네이버예약/네이버로" → naver_reservation
   - "카카오톡 선물" → kakao_gift
6. 앱을 지정하지 않으면 app_preference는 null (라우터가 기본값 사용)
"""

PARSE_INTENT_TOOL = {
    "name": "parse_intent",
    "description": "사용자 발화에서 인텐트를 파싱합니다",
    "input_schema": {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "enum": ["shopping", "delivery", "mobility", "travel", "reservation", "gift"],
            },
            "action": {
                "type": "string",
                "enum": ["order", "search", "book", "reserve", "cancel", "compare", "recommend"],
            },
            "entities": {"type": "object"},
            "minitap_goal": {
                "type": "string",
                "description": "Minitap 에이전트에게 전달할 자연어 목표 (한국어, 상세하게)",
            },
            "app_preference": {
                "type": ["string", "null"],
                "description": (
                    "사용자가 특정 앱을 지정한 경우 앱 키. 예: coupang, naver_shopping, baemin, coupang_eats, "
                    "kakaot, yanolja, catchtable, naver_reservation, kakao_gift. 지정하지 않으면 null."
                ),
                "enum": [
                    "coupang",
                    "naver_shopping",
                    "baemin",
                    "coupang_eats",
                    "kakaot",
                    "yanolja",
                    "catchtable",
                    "naver_reservation",
                    "kakao_gift",
                    None,
                ],
            },
            "needs_clarification": {"type": "boolean"},
            "clarification_question": {"type": ["string", "null"]},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        },
        "required": ["category", "action", "entities", "minitap_goal", "needs_clarification", "confidence"],
    },
}
