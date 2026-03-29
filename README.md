# DDalkkak (딸깍) — "딸깍 한 번으로 주문/예약 완료"

자연어 입력을 통해 한국의 다양한 로컬 서비스(쇼핑, 배달, 택시, 여행, 예약, 선물)를 자동으로 처리하는 AI 에이전트입니다.

## 🚀 주요 기능
- **자연어 인텐트 분석**: Claude LLM을 사용하여 사용자의 의도를 파악하고 필요한 정보를 추출합니다.
- **서비스 라우팅**: 분석된 의도에 따라 최적의 앱(쿠팡, 배민, 카카오T 등)을 선택합니다.
- **물리 기기 자동화**: Minitap Mobile Use SDK를 통해 실제 iPhone에서 작업을 수행합니다.
- **안전 가드레일**: 모든 작업 완료 후 즉시 취소 기능을 포함하여 테스트 안전성을 보장합니다.

## 🏗️ 아키텍처

```
┌─────────────────────┐
│   User (CLI/카톡)    │
│  "샴푸 주문해줘"      │
└──────────┬──────────┘
           │ Phase 1: CLI (stdin/stdout)
           │ Phase 2: KakaoTalk API (optional)
           ▼
┌─────────────────────┐
│   Interface Layer   │
│   (CLI first,       │
│    KakaoTalk later) │
└──────────┬──────────┘
           │ user message + session context
           ▼
┌─────────────────────┐
│  Intent Parser      │
│  (Claude API with   │
│   tool_use)         │
│                     │
│  Input: 자연어 텍스트  │
│  Output: {          │
│    category,        │
│    action,          │
│    entities,        │
│    app_target,      │
│    minitap_goal     │
│  }                  │
└──────────┬──────────┘
           │ ParsedIntent
           ▼
┌─────────────────────┐
│  Conversation       │
│  State Manager      │
│  (in-memory dict)   │
│                     │
│  - slot filling     │
│  - multi-turn       │
│  - user preferences │
└──────────┬──────────┘
           │ resolved intent (all slots filled)
           ▼
┌─────────────────────┐
│  Service Router     │
│                     │
│  category → handler │
│  handler → app_id   │
│  handler → goal     │
└──────────┬──────────┘
           │ MinitapTaskConfig
           ▼
┌─────────────────────┐
│  Minitap Agent      │
│  Wrapper            │
│                     │
│  - init agent       │
│  - lock to app      │
│  - run_task(goal)   │
│  - get_screenshot   │
│  - trace recording  │
│  - error handling   │
└──────────┬──────────┘
           │ USB + WDA
           ▼
┌─────────────────────┐
│  Physical iPhone    │
│                     │
│  쿠팡 | 배민 | 쿠팡이츠│
│  카카오T | 네이버     │
│  야놀자 | 여기어때    │
│  캐치테이블 | 카카오톡  │
└─────────────────────┘
```

## 🛠️ 사전 요구사항
- **Python 3.12+**
- **uv** (패키지 매니저)
- **물리 iPhone** (USB 연결 필요)
- **macOS** (WDA 빌드 및 실행용)
- **Appium + XCUITest Driver**
- **Claude API Key** (Anthropic)

## ⚙️ 환경 설정
`.env` 파일을 생성하고 다음 변수들을 설정해야 합니다.

```bash
# Claude API
ANTHROPIC_API_KEY=sk-ant-xxxxx

# iOS App Bundle IDs
COUPANG_BUNDLE_ID=com.coupang.Coupang
BAEMIN_BUNDLE_ID=com.woowahan.deliveryapp
COUPANG_EATS_BUNDLE_ID=com.coupang.CoupangEats
KAKAOT_BUNDLE_ID=com.kakao.taxi
NAVER_BUNDLE_ID=com.nhn.NaverSearch
YANOLJA_BUNDLE_ID=com.yanolja.yanoljaapp
CATCHTABLE_BUNDLE_ID=com.catchtable.catchtable
KAKAO_BUNDLE_ID=com.kakao.talk
```

## 🏃 실행 방법
1. 의존성 설치:
   ```bash
   uv sync
   ```
2. CLI 앱 실행:
   ```bash
   uv run python -m src.main
   ```

## 📱 지원 서비스 목록
| 카테고리 | 서비스 |
|----------|---------|
| 🛒 쇼핑 | 쿠팡, 네이버쇼핑 |
| 🍔 배달 | 배달의민족, 쿠팡이츠 |
| 🚕 모빌리티 | 카카오T |
| ✈️ 여행 | 야놀자 |
| 🍽️ 예약 | 캐치테이블, 네이버예약 |
| 🎁 선물 | 카카오톡 선물하기 |

## 💬 실행 예시
- "샴푸 다 떨어졌다. 주문해줘"
- "오늘 저녁 혼자 먹을 거 추천해서 주문해줘"
- "내일 아침 7시에 공항 가는 택시 잡아줘"
- "이번 주말 제주도 숙소 예약해줘"
- "근처 맛집 예약해줘"
- "부모님 집으로 과일 선물 보내줘"
