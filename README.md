# DDalkkak (딸깍) — "딸깍 한 번으로 주문/예약 완료"

자연어 입력을 통해 한국의 다양한 로컬 서비스(쇼핑, 배달, 택시, 여행, 예약, 선물)를 자동으로 처리하는 AI 에이전트입니다.

## 주요 기능
- **자연어 인텐트 분석**: Claude LLM으로 사용자 의도와 엔티티를 추출합니다.
- **서비스 라우팅**: 의도에 따라 앱(쿠팡, 배민, 카카오T 등)을 선택합니다.
- **Android 자동화**: [Droidrun](https://docs.droidrun.ai/quickstart) SDK + Portal 앱으로 에뮬레이터/실기기에서 UI를 제어합니다.
- **안전 가드레일**: 목표 문구에 즉시 취소 등 안전 지시를 포함합니다.

## 아키텍처

```
User (CLI) → Intent Parser (Claude) → Conversation → Router → ServiceHandler
    → DroidRunAgent (Droidrun DroidAgent + Portal) → Android (ADB)
```

## 사전 요구사항
- **Python 3.12+**, **uv**
- **Android 에뮬레이터 또는 USB 기기**, **ADB**
- **Droidrun Portal**: `droidrun setup` 후 `droidrun ping` 성공
- **ANTHROPIC_API_KEY** (인텐트 파싱 + Droidrun 에이전트용 Claude)

## 환경 설정

`.env` 예시:

```bash
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Android 패키지명 (필요 시 `adb shell pm list packages` 로 확인 후 수정)
COUPANG_PACKAGE=com.coupang.mobile
BAEMIN_PACKAGE=com.baemin
COUPANG_EATS_PACKAGE=com.coupang.coupangeats
KAKAOT_PACKAGE=com.kakao.taxi
NAVER_PACKAGE=com.nhn.android.search
YANOLJA_PACKAGE=com.yanolja.local
CATCHTABLE_PACKAGE=co.catchtable.catchtable
KAKAO_PACKAGE=com.kakao.talk

DEVICE_SERIAL=emulator-5554
```

## 실행

```bash
uv sync
uv run python -m src.main
```

연결 테스트: `uv run python test.py` (스크린샷 저장)

## 지원 서비스

| 카테고리 | 앱 |
|----------|-----|
| 쇼핑 | 쿠팡, 네이버쇼핑 |
| 배달 | 배달의민족, 쿠팡이츠 |
| 모빌리티 | 카카오T |
| 여행 | 야놀자 |
| 예약 | 캐치테이블, 네이버예약 |
| 선물 | 카카오톡 선물하기 |

## 실행 예시
- "샴푸 다 떨어졌다. 주문해줘"
- "오늘 저녁 혼자 먹을 거 추천해서 주문해줘"
- "내일 아침 7시에 공항 가는 택시 잡아줘"
