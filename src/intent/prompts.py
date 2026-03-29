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

엔티티 추출 가이드 (카테고리별 필수 필드):
- shopping: product(필수), brand, quantity, price_range, use_previous_order
- delivery: cuisine(음식 종류), restaurant(가게 이름), price_range, solo_or_group, time
- mobility: destination(필수), pickup_time, vehicle_type
- travel: destination(필수), dates, accommodation_type, budget, num_guests
- reservation: cuisine(양식/한식/일식/중식 등), venue_name(특정 식당명), location(지역),
  party_size(인원수), reservation_date(날짜 예: "4월 4일"), reservation_time(시간 예: "오후 6시")
- gift: recipient(필수), occasion, item_type, budget, delivery_address

reservation 엔티티 주의사항:
- "양식" "한식" "일식" 등 음식 종류는 반드시 cuisine에 추출
- 날짜와 시간은 reservation_date와 reservation_time으로 분리 추출
- "여자친구랑" = party_size: 2, "4명이서" = party_size: 4
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
            "entities": {
                "type": "object",
                "description": (
                    "카테고리별 엔티티. "
                    "reservation: {cuisine, venue_name, location, party_size, reservation_date, reservation_time}. "
                    "delivery: {cuisine, restaurant, price_range, solo_or_group, time}. "
                    "shopping: {product, brand, quantity, price_range, use_previous_order}. "
                    "mobility: {destination, pickup_time, vehicle_type}. "
                    "travel: {destination, dates, accommodation_type, budget, num_guests}. "
                    "gift: {recipient, occasion, item_type, budget, delivery_address}."
                ),
            },
            "minitap_goal": {
                "type": "string",
                "description": "에이전트에게 전달할 자연어 목표 (한국어, 상세하게)",
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
