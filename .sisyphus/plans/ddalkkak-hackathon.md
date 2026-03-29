# DDalkkak (딸깍) — Hackathon Execution Plan

> "딸깍 한 번으로 주문/예약 완료"
> Natural language → Intent parsing → Service routing → Minitap physical iPhone automation → Real transaction

## Overview

| Field | Value |
|-------|-------|
| **Project** | DDalkkak — AI agent that completes orders/reservations on Korean local services |
| **Architecture** | CLI → Claude LLM Intent Parser → Service Router → Minitap Agent → Physical iPhone |
| **Language** | Python 3.12+ |
| **Package Manager** | uv (replaces pip/venv) |
| **Linting/Formatting** | ruff (linter + formatter) |
| **Type Checking** | ty |
| **LLM** | Claude API (Anthropic) with tool_use / function calling |
| **UI (Phase 1)** | CLI — 터미널 기반 대화형 인터페이스 (MVP, 먼저 검증) |
| **UI (Phase 2)** | KakaoTalk 챗봇 — Phase 1 검증 완료 후 optional 추가 |
| **Automation** | Minitap Mobile Use SDK — physical iOS device via USB + WDA |
| **Repo State** | Greenfield (empty repo, only README.md exists) |
| **Execution** | Ralph loop — 5 hours unattended, produces complete working prototype |

## Architecture Diagram

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

## Target Services & iOS App Bundle IDs

| Category | Service | iOS Bundle ID (verify in pre-work) | Test Strategy |
|----------|---------|-----------------------------------|---------------|
| 🛒 쇼핑 | 쿠팡 | `com.coupang.Coupang` | **실제 주문 → 즉시 주문취소** (배송 전) |
| 🛒 쇼핑 | 네이버쇼핑 | `com.nhn.NaverSearch` | **실제 주문 → 즉시 주문취소** |
| 🍔 배달 | 배달의민족 | `com.woowahan.deliveryapp` | **실제 주문 → 즉시 주문취소** (조리 전) |
| 🍔 배달 | 쿠팡이츠 | `com.coupang.CoupangEats` | **실제 주문 → 즉시 주문취소** (조리 전) |
| 🚕 모빌리티 | 카카오T | `com.kakao.taxi` | **실제 호출 → 즉시 취소** (5분 쿨다운 주의) |
| ✈️ 여행 | 야놀자 | `com.yanolja.yanoljaapp` | **무료취소 상품 실제 예약 → 즉시 취소** |
| 🍽️ 예약 | 캐치테이블 | `com.catchtable.catchtable` | **실제 예약 → 즉시 취소** |
| 🍽️ 예약 | 네이버예약 | `com.nhn.NaverSearch` | **실제 예약 → 즉시 취소** |
| 🎁 선물 | 카카오톡 선물하기 | `com.kakao.talk` | **실제 선물 전송 → 수신 전 즉시 취소** |

> ⚠️ Bundle ID는 사전 작업에서 실제 iPhone에서 확인 필수. 위는 추정값.

## Intent Schema (6 Categories)

```python
# Each intent parsed by Claude will conform to this structure
class ParsedIntent:
    category: Literal["shopping", "delivery", "mobility", "travel", "reservation", "gift"]
    action: Literal["order", "search", "book", "reserve", "cancel", "compare", "recommend"]
    entities: dict  # product, destination, time, recipient, budget, etc.
    app_target: str  # resolved app name (e.g., "coupang", "baemin")
    minitap_goal: str  # natural language goal for Minitap agent
    needs_clarification: bool
    clarification_question: Optional[str]
```

### Category-specific entity schemas:
- **shopping**: product, brand, quantity, price_range, previous_order_ref
- **delivery**: cuisine, restaurant, price_range, solo/group, time
- **mobility**: destination, pickup_time, vehicle_type
- **travel**: destination, dates, accommodation_type, budget, num_guests
- **reservation**: cuisine_type, location, party_size, time, restaurant_name
- **gift**: recipient, occasion, item_type, budget, delivery_address

---

## PART A: PRE-WORK CHECKLIST (Manual — Before Ralph Loop)

> ⏱️ 예상 소요: 30-60분
> 🎯 목적: Ralph loop가 코드 작성에만 집중할 수 있도록, 물리적/환경적 셋업을 완료

### A1. macOS 환경 확인

```bash
# 1. Python 3.12+ 확인
python3 --version  # 3.12 이상이어야 함

# 2. Node.js + npm 확인 (Appium 설치용)
node --version
npm --version

# 3. Xcode CLI Tools 확인
xcode-select --print-path  # /Applications/Xcode.app/Contents/Developer 등

# 4. Homebrew (iproxy용)
brew --version
```

**미설치 시:**
```bash
# Python 3.12
brew install python@3.12

# Node.js
brew install node

# Xcode CLI Tools
xcode-select --install
```

### A2. Appium + WDA 설치 (One-time)

```bash
# 1. Appium 글로벌 설치
npm install -g appium

# 2. XCUITest 드라이버 설치 (WDA 포함)
appium driver install xcuitest

# 3. WDA 경로 확인
ls ~/.appium/node_modules/appium-xcuitest-driver/node_modules/appium-webdriveragent/
# WebDriverAgent.xcodeproj 파일이 보여야 함
```

### A3. WDA Code Signing (Xcode에서)

```
1. Xcode로 WebDriverAgent.xcodeproj 열기:
   open ~/.appium/node_modules/appium-xcuitest-driver/node_modules/appium-webdriveragent/WebDriverAgent.xcodeproj

2. Signing 설정 (3개 타겟 모두):
   - WebDriverAgentRunner → Signing & Capabilities
     → Automatic Signing 활성화
     → Team 선택 (Apple ID)
     → Bundle Identifier를 고유값으로 변경 (예: com.yourname.WebDriverAgentRunner)
   - WebDriverAgentLib → 동일하게
   - IntegrationApp → 동일하게

3. iPhone을 USB로 연결

4. Destination에서 연결된 iPhone 선택

5. IntegrationApp 빌드 (프로비저닝 프로파일 설치됨)
   - Product → Build (⌘B)

6. iPhone에서 개발자 인증서 신뢰:
   설정 → 일반 → VPN 및 기기 관리 → 개발자 앱 → 신뢰
```

### A4. iPhone 앱 설치 + 로그인

**설치 필요 앱 목록 (8개):**
- [ ] 쿠팡
- [ ] 배달의민족
- [ ] 쿠팡이츠
- [ ] 카카오T
- [ ] 네이버 앱
- [ ] 야놀자
- [ ] 캐치테이블
- [ ] 카카오톡

**각 앱에서:**
- [ ] 로그인 완료
- [ ] 결제수단 등록 (테스트용)
- [ ] 알림 설정 (팝업 방지용 — 알림 off 권장)
- [ ] 자동 잠금 해제: 설정 → 디스플레이 → 자동 잠금 → "안 함"

### A5. Bundle ID 확인

iPhone을 Mac에 USB로 연결한 상태에서:
```bash
# ideviceinstaller로 설치된 앱 목록 + bundle ID 확인
brew install ideviceinstaller
ideviceinstaller -l
```
→ 각 앱의 실제 bundle ID를 메모하여 `.env`에 기록

### A6. Minitap SDK 설치 + 연결 테스트

```bash
# 1. 가상환경 생성
python3.12 -m venv .venv
source .venv/bin/activate

# 2. Minitap SDK 설치
pip install minitap-mobile-use

# 3. 연결 테스트 스크립트 실행
python3 -c "
import asyncio
from minitap.mobile_use.sdk import Agent

async def test():
    agent = Agent()
    ok = await agent.init()
    print(f'Agent initialized: {ok}')
    screenshot = await agent.get_screenshot()
    screenshot.save('test_screenshot.png')
    print('Screenshot saved to test_screenshot.png')
    await agent.clean()
    print('Agent cleaned up')

asyncio.run(test())
"

# 4. test_screenshot.png 확인 — iPhone 화면이 캡처되어야 함
```

### A7. API Keys 준비

```bash
# .env 파일 생성 (Ralph loop이 읽을 수 있도록)
cat > .env << 'EOF'
# Claude API
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Minitap (Platform 사용 시, 로컬은 불필요)
# MINITAP_API_KEY=xxxxx

# iOS App Bundle IDs (A5에서 확인한 실제 값으로 교체)
COUPANG_BUNDLE_ID=com.coupang.Coupang
BAEMIN_BUNDLE_ID=com.woowahan.deliveryapp
COUPANG_EATS_BUNDLE_ID=com.coupang.CoupangEats
KAKAOT_BUNDLE_ID=com.kakao.taxi
NAVER_BUNDLE_ID=com.nhn.NaverSearch
YANOLJA_BUNDLE_ID=com.yanolja.yanoljaapp
CATCHTABLE_BUNDLE_ID=com.catchtable.catchtable
KAKAO_BUNDLE_ID=com.kakao.talk
EOF
```

### A8. uv 설치 확인

```bash
# uv 설치 확인
uv --version  # 0.5+ 이어야 함

# 미설치 시
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### A9. 사전 작업 검증 체크리스트

```
□ Python 3.12+ 설치됨
□ Node.js + npm 설치됨
□ Appium + xcuitest 드라이버 설치됨
□ WDA code signing 완료 (Xcode에서 빌드 성공)
□ iPhone USB 연결 + Mac 신뢰됨
□ iPhone 자동 잠금 = "안 함"
□ 모든 앱 설치 + 로그인 완료
□ Bundle ID 확인하여 .env에 기록
□ Minitap SDK 테스트 성공 (스크린샷 저장됨)
□ .env 파일 생성됨 (API keys + bundle IDs)
□ uv 설치됨
□ .venv 가상환경 생성됨 (uv가 자동 관리)
```

---

## PART B: RALPH LOOP SEED SPEC (5h Unattended Build)

> Ralph가 빈 레포에서 시작하여 아래 모든 Wave를 순서대로 완성합니다.
> 각 Task는 acceptance criteria를 만족해야 다음으로 진행합니다.

### Project Structure (Ralph가 생성할 디렉토리 구조)

```
DDalkkak/
├── .env                    # (pre-work에서 생성됨)
├── .env.example            # 환경변수 템플릿
├── .gitignore
├── pyproject.toml          # Python 프로젝트 설정
├── uv.lock                 # uv lockfile (자동 생성)
├── README.md               # 프로젝트 문서
├── src/
│   ├── __init__.py
│   ├── main.py             # 엔트리포인트 (Telegram bot 시작)
│   ├── config.py           # 환경변수 로딩 + 설정 관리
│   ├── intent/
│   │   ├── __init__.py
│   │   ├── parser.py       # Claude API 인텐트 파서
│   │   ├── schemas.py      # 인텐트 스키마 정의 (Pydantic)
│   │   └── prompts.py      # Claude 시스템 프롬프트 + 도구 정의
│   ├── router/
│   │   ├── __init__.py
│   │   └── router.py       # 인텐트 → 서비스 라우팅
│   ├── services/
│   │   ├── __init__.py
│   │   ├── base.py         # 서비스 핸들러 베이스 클래스
│   │   ├── shopping.py     # 쇼핑 (쿠팡, 네이버쇼핑)
│   │   ├── delivery.py     # 배달 (배민, 쿠팡이츠)
│   │   ├── mobility.py     # 모빌리티 (카카오T)
│   │   ├── travel.py       # 여행 (야놀자, 여기어때)
│   │   ├── reservation.py  # 예약 (캐치테이블, 네이버예약)
│   │   └── gift.py         # 선물 (카카오톡 선물하기)
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── minitap_agent.py  # Minitap SDK 래퍼
│   │   └── task_builder.py   # Minitap TaskRequest 빌더
│   ├── cli/
│   │   ├── __init__.py
│   │   └── app.py             # CLI 대화형 인터페이스 (Phase 1)
│   ├── kakao/                  # (Optional — Phase 2)
│   │   ├── __init__.py
│   │   └── chatbot.py          # 카카오톡 챗봇 연동
│   └── state/
│       ├── __init__.py
│       └── conversation.py   # 대화 상태 관리 (in-memory)
├── tests/
│   ├── __init__.py
│   ├── test_parser.py
│   ├── test_router.py
│   ├── test_services.py
│   ├── test_agent.py
│   └── test_conversation.py
└── scripts/
    ├── test_minitap.py       # Minitap 연결 테스트
    └── demo.py               # 데모 시나리오 스크립트
```

### Dependencies (requirements.txt)

```
anthropic>=0.40.0
minitap-mobile-use
pydantic>=2.0
pydantic-settings>=2.0
python-dotenv>=1.0
Pillow>=10.0
pytest>=8.0
pytest-asyncio>=0.24.0
ruff>=0.9.0
ty>=0.0.1
```

---

## Wave 1: Foundation (예상 30분)

### Task 1.1: Repository Bootstrap (uv + ruff + ty)
- **Category**: `quick`
- **Skills**: `git-master`
- **What**: uv 기반 프로젝트 기본 구조 생성
- **Files to create**:
  - `.gitignore` — Python, .venv, .env, __pycache__, traces/, *.png, .DS_Store
  - `pyproject.toml` — uv 프로젝트 설정 + ruff/ty 설정 포함:
    ```toml
    [project]
    name = "ddalkkak"
    version = "0.1.0"
    requires-python = ">=3.12"
    dependencies = [
        "anthropic>=0.40.0",
        "minitap-mobile-use",
        "pydantic>=2.0",
        "pydantic-settings>=2.0",
        "python-dotenv>=1.0",
        "Pillow>=10.0",
    ]

    [project.optional-dependencies]
    dev = [
        "pytest>=8.0",
        "pytest-asyncio>=0.24.0",
        "ruff>=0.9.0",
        "ty>=0.0.1",
    ]

    [tool.ruff]
    line-length = 120
    target-version = "py312"

    [tool.ruff.lint]
    select = ["E", "F", "I", "N", "W", "UP", "B", "SIM"]

    [tool.ruff.format]
    quote-style = "double"

    [tool.ty]
    python-version = "3.12"
    ```
  - `.env.example` — 모든 환경변수 키를 빈 값으로
  - `src/__init__.py` — empty
  - `tests/__init__.py` — empty
- **Commands to run**:
  ```bash
  uv init --name ddalkkak  # 또는 직접 pyproject.toml 생성
  uv sync  # 의존성 설치 + lockfile 생성
  uv run ruff check .  # lint 확인
  ```
- **Acceptance Criteria**:
  - `uv run python -c "import src"` 성공
  - `.gitignore`에 `.env`, `__pycache__`, `traces/`, `.venv` 포함
  - `uv sync` 성공 (lockfile 생성됨)
  - `uv run ruff check .` 에러 없음
- **QA Scenario**: `ls src/ tests/ .gitignore pyproject.toml uv.lock .env.example` 모두 존재 확인

### Task 1.2: Configuration Module
- **Category**: `quick`
- **Skills**: `git-master`
- **What**: 환경변수 로딩 + 타입 안전 설정 관리
- **Files to create**:
  - `src/config.py`
- **Implementation**:
  ```python
  # src/config.py
  from pydantic_settings import BaseSettings
  
  class Settings(BaseSettings):
      anthropic_api_key: str
      minitap_api_key: str = ""  # optional for local mode
      
      # iOS App Bundle IDs
      coupang_bundle_id: str = "com.coupang.Coupang"
      baemin_bundle_id: str = "com.woowahan.deliveryapp"
      coupang_eats_bundle_id: str = "com.coupang.CoupangEats"
      kakaot_bundle_id: str = "com.kakao.taxi"
      naver_bundle_id: str = "com.nhn.NaverSearch"
      yanolja_bundle_id: str = "com.yanolja.yanoljaapp"
      catchtable_bundle_id: str = "com.catchtable.catchtable"
      kakao_bundle_id: str = "com.kakao.talk"
      
      # Minitap settings
      minitap_max_steps: int = 400
      minitap_task_interval_seconds: int = 5
      
      class Config:
          env_file = ".env"
  
  settings = Settings()
  ```
- **Acceptance Criteria**:
  - `.env`가 있으면 설정 로딩 성공
  - `.env`가 없으면 ValidationError 발생 (필수 키 누락)
  - `from src.config import settings` 성공
- **QA Scenario**: `python3 -c "from src.config import settings; print(settings.model_dump())"` 실행하여 설정값 출력 확인

### Task 1.3: README 업데이트
- **Category**: `quick`
- **Skills**: `git-master`
- **What**: 프로젝트 개요, 아키텍처, 실행 방법 문서화
- **Content**:
  - 프로젝트 설명 (한국어)
  - 아키텍처 다이어그램 (위 Architecture Diagram 섹션 참조)
  - 사전 요구사항 (Python 3.12+, iPhone, Minitap, etc.)
  - 실행 방법: `python -m src.main`
  - 환경변수 설명
  - 지원 서비스 목록
- **Acceptance Criteria**: README.md에 위 모든 섹션 포함

## Wave 2: Core Intent Pipeline (예상 60분)

### Task 2.1: Intent Schema Definition (Pydantic)
- **Category**: `deep`
- **Skills**: `git-master`
- **What**: 6개 카테고리에 대한 Pydantic 스키마 정의
- **Files to create**:
  - `src/intent/__init__.py`
  - `src/intent/schemas.py`
- **Implementation**:
  ```python
  # src/intent/schemas.py
  from pydantic import BaseModel, Field
  from typing import Optional, Literal
  from enum import Enum

  class ServiceCategory(str, Enum):
      SHOPPING = "shopping"
      DELIVERY = "delivery"
      MOBILITY = "mobility"
      TRAVEL = "travel"
      RESERVATION = "reservation"
      GIFT = "gift"

  class ServiceAction(str, Enum):
      ORDER = "order"
      SEARCH = "search"
      BOOK = "book"
      RESERVE = "reserve"
      CANCEL = "cancel"
      COMPARE = "compare"
      RECOMMEND = "recommend"

  class ShoppingEntities(BaseModel):
      product: str
      brand: Optional[str] = None
      quantity: int = 1
      price_range: Optional[str] = None
      use_previous_order: bool = False

  class DeliveryEntities(BaseModel):
      cuisine: Optional[str] = None
      restaurant: Optional[str] = None
      menu_items: list[str] = Field(default_factory=list)
      for_how_many: int = 1
      price_range: Optional[str] = None

  class MobilityEntities(BaseModel):
      destination: str
      pickup_location: Optional[str] = None
      pickup_time: Optional[str] = None  # ISO format or natural language
      vehicle_type: Optional[str] = None  # 택시, 블랙, 벤티 등

  class TravelEntities(BaseModel):
      destination: str
      check_in: Optional[str] = None
      check_out: Optional[str] = None
      accommodation_type: Optional[str] = None  # 호텔, 펜션, 리조트 등
      num_guests: int = 1
      budget: Optional[str] = None

  class ReservationEntities(BaseModel):
      cuisine_type: Optional[str] = None
      restaurant_name: Optional[str] = None
      location: Optional[str] = None
      party_size: int = 1
      reservation_time: Optional[str] = None

  class GiftEntities(BaseModel):
      recipient: str
      occasion: Optional[str] = None
      item_type: Optional[str] = None
      budget: Optional[str] = None
      delivery_address: Optional[str] = None

  class ParsedIntent(BaseModel):
      category: ServiceCategory
      action: ServiceAction
      entities: dict  # category-specific entities
      app_target: Optional[str] = None  # resolved by router
      minitap_goal: str  # natural language goal for Minitap
      needs_clarification: bool = False
      clarification_question: Optional[str] = None
      confidence: float = Field(default=1.0, ge=0.0, le=1.0)
  ```
- **Acceptance Criteria**:
  - `from src.intent.schemas import ParsedIntent, ServiceCategory` 성공
  - 모든 6개 카테고리에 entity 클래스 존재
  - ParsedIntent가 JSON serializable
- **QA Scenario**: `pytest tests/test_parser.py::test_schema_serialization` 통과

### Task 2.2: Claude Intent Parser
- **Category**: `deep`
- **Skills**: `git-master`
- **What**: Claude API tool_use를 이용한 한국어 인텐트 파싱 엔진
- **Files to create**:
  - `src/intent/prompts.py`
  - `src/intent/parser.py`
- **Implementation guidance for prompts.py**:
  ```python
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
  """
  
  PARSE_INTENT_TOOL = {
      "name": "parse_intent",
      "description": "사용자 발화에서 인텐트를 파싱합니다",
      "input_schema": {
          "type": "object",
          "properties": {
              "category": {"type": "string", "enum": ["shopping", "delivery", "mobility", "travel", "reservation", "gift"]},
              "action": {"type": "string", "enum": ["order", "search", "book", "reserve", "cancel", "compare", "recommend"]},
              "entities": {"type": "object"},
              "minitap_goal": {"type": "string", "description": "Minitap 에이전트에게 전달할 자연어 목표 (한국어, 상세하게)"},
              "needs_clarification": {"type": "boolean"},
              "clarification_question": {"type": "string"},
              "confidence": {"type": "number", "minimum": 0, "maximum": 1}
          },
          "required": ["category", "action", "entities", "minitap_goal", "needs_clarification", "confidence"]
      }
  }
  ```
- **Implementation guidance for parser.py**:
  ```python
  import anthropic
  from src.config import settings
  from src.intent.schemas import ParsedIntent
  from src.intent.prompts import SYSTEM_PROMPT, PARSE_INTENT_TOOL
  
  class IntentParser:
      def __init__(self):
          self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
      
      async def parse(self, user_message: str, context: dict = None) -> ParsedIntent:
          """한국어 자연어를 ParsedIntent로 변환"""
          messages = []
          if context and context.get("history"):
              for msg in context["history"][-5:]:  # last 5 turns
                  messages.append(msg)
          messages.append({"role": "user", "content": user_message})
          
          response = self.client.messages.create(
              model="claude-sonnet-4-20250514",
              max_tokens=1024,
              system=SYSTEM_PROMPT,
              tools=[PARSE_INTENT_TOOL],
              messages=messages
          )
          
          # Extract tool_use result
          for block in response.content:
              if block.type == "tool_use" and block.name == "parse_intent":
                  return ParsedIntent(**block.input)
          
          raise ValueError("Failed to parse intent from Claude response")
  ```
- **Acceptance Criteria**:
  - `parser.parse("샴푸 다 떨어졌다. 주문해줘")` → category="shopping", action="order"
  - `parser.parse("오늘 저녁 혼자 먹을 거 추천해서 주문해줘")` → category="delivery"
  - `parser.parse("내일 아침 7시에 공항 가는 택시 잡아줘")` → category="mobility"
  - `parser.parse("이번 주말 제주도 숙소 예약해줘")` → category="travel"
  - `parser.parse("근처 맛집 예약해줘")` → category="reservation"
  - `parser.parse("부모님 집으로 과일 선물 보내줘")` → category="gift"
- **QA Scenario**: `pytest tests/test_parser.py` — 6개 카테고리 각 1개 이상 테스트 통과
- **Depends on**: Task 2.1

### Task 2.3: Service Router
- **Category**: `deep`
- **Skills**: `git-master`
- **What**: ParsedIntent → 앱 타겟 + Minitap goal 매핑
- **Files to create**:
  - `src/router/__init__.py`
  - `src/router/router.py`
- **Implementation guidance**:
  ```python
  from src.intent.schemas import ParsedIntent, ServiceCategory
  from src.config import settings
  
  # Category → (primary_app, bundle_id, app_name)
  SERVICE_MAP = {
      ServiceCategory.SHOPPING: [
          ("coupang", settings.coupang_bundle_id, "쿠팡"),
          ("naver_shopping", settings.naver_bundle_id, "네이버쇼핑"),
      ],
      ServiceCategory.DELIVERY: [
          ("baemin", settings.baemin_bundle_id, "배달의민족"),
          ("coupang_eats", settings.coupang_eats_bundle_id, "쿠팡이츠"),
      ],
      ServiceCategory.MOBILITY: [
          ("kakaot", settings.kakaot_bundle_id, "카카오T"),
      ],
      ServiceCategory.TRAVEL: [
          ("yanolja", settings.yanolja_bundle_id, "야놀자"),
      ],
      ServiceCategory.RESERVATION: [
          ("catchtable", settings.catchtable_bundle_id, "캐치테이블"),
          ("naver_reservation", settings.naver_bundle_id, "네이버예약"),
      ],
      ServiceCategory.GIFT: [
          ("kakao_gift", settings.kakao_bundle_id, "카카오톡 선물하기"),
      ],
  }
  
  class ServiceRouter:
      def route(self, intent: ParsedIntent) -> tuple[str, str, str]:
          """Returns (app_key, bundle_id, display_name)"""
          services = SERVICE_MAP.get(intent.category, [])
          if not services:
              raise ValueError(f"No service mapping for {intent.category}")
          # Default: first service in list (primary)
          # TODO: Extend with price comparison logic
          return services[0]
  ```
- **Acceptance Criteria**:
  - shopping intent → coupang bundle ID 반환
  - delivery intent → baemin bundle ID 반환
  - 모든 6개 카테고리 라우팅 성공
- **QA Scenario**: `pytest tests/test_router.py` — 6개 카테고리 라우팅 테스트 통과
- **Depends on**: Task 2.1

## Wave 3: Minitap Agent Layer (예상 60분)

### Task 3.1: Minitap Agent Wrapper
- **Category**: `deep`
- **Skills**: `git-master`
- **What**: Minitap SDK를 감싸는 고수준 래퍼 — 앱 잠금, task 실행, 스크린샷, 에러 핸들링
- **Files to create**:
  - `src/agent/__init__.py`
  - `src/agent/minitap_agent.py`
- **Implementation guidance**:
  ```python
  import asyncio
  from pathlib import Path
  from datetime import datetime
  from minitap.mobile_use.sdk import Agent
  from minitap.mobile_use.sdk.types import TaskRequest
  from src.config import settings
  
  class MinitapAgentWrapper:
      def __init__(self):
          self.agent: Agent | None = None
          self._initialized = False
      
      async def initialize(self) -> bool:
          """WDA 초기화 + 디바이스 연결"""
          if self._initialized:
              return True
          self.agent = Agent()
          ok = await self.agent.init()
          self._initialized = ok
          return ok
      
      async def execute_task(
          self,
          goal: str,
          bundle_id: str,
          max_steps: int = None,
          trace_path: str = None,
      ) -> dict:
          """앱을 잠그고 자연어 goal 실행"""
          if not self._initialized:
              await self.initialize()
          
          max_steps = max_steps or settings.minitap_max_steps
          trace_dir = Path(trace_path or f"traces/{datetime.now().strftime('%Y%m%d_%H%M%S')}")
          trace_dir.mkdir(parents=True, exist_ok=True)
          
          task = self.agent.new_task(goal) \
              .with_locked_app_package(bundle_id) \
              .with_max_steps(max_steps) \
              .with_trace_recording(enabled=True, path=str(trace_dir)) \
              .build()
          
          result = await self.agent.run_task(request=task)
          
          # Rate limiting between tasks
          await asyncio.sleep(settings.minitap_task_interval_seconds)
          
          return {
              "success": True,
              "result": str(result),
              "trace_path": str(trace_dir),
          }
      
      async def take_screenshot(self) -> str:
          """현재 화면 캡처"""
          if not self._initialized:
              await self.initialize()
          img = await self.agent.get_screenshot()
          path = f"screenshots/{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
          Path(path).parent.mkdir(parents=True, exist_ok=True)
          img.save(path)
          return path
      
      async def cleanup(self):
          """리소스 정리"""
          if self.agent:
              await self.agent.clean()
              self._initialized = False
      
      async def health_check(self) -> bool:
          """디바이스 연결 상태 확인"""
          try:
              if not self._initialized:
                  return False
              await self.agent.get_screenshot()
              return True
          except Exception:
              return False
  ```
- **Acceptance Criteria**:
  - `agent.initialize()` 성공 (iPhone 연결됨)
  - `agent.take_screenshot()` 성공 (스크린샷 저장됨)
  - `agent.execute_task(goal="홈 화면에서 설정 앱 열기", bundle_id="com.apple.Preferences")` 성공
  - `agent.cleanup()` 에러 없이 완료
- **QA Scenario**: `pytest tests/test_agent.py` — initialize, screenshot, cleanup 테스트 통과
- **Depends on**: Task 1.2

### Task 3.2: Task Builder Helper
- **Category**: `quick`
- **Skills**: `git-master`
- **What**: 각 서비스 카테고리별 Minitap goal 생성 헬퍼
- **Files to create**:
  - `src/agent/task_builder.py`
- **Implementation guidance**:
  ```python
  from src.intent.schemas import ParsedIntent, ServiceCategory
  
  class TaskGoalBuilder:
      """ParsedIntent를 Minitap-optimized goal 문장으로 변환"""
      
      @staticmethod
      def build_goal(intent: ParsedIntent) -> str:
          """인텐트의 minitap_goal을 서비스 맥락에 맞게 보강"""
          base_goal = intent.minitap_goal
          
          # 카테고리별 추가 지시사항: 실제 결제/예약 완료 후 즉시 취소
          safety_suffixes = {
              ServiceCategory.SHOPPING: "결제를 완료하세요. 주문 완료 후 '주문내역'에서 해당 주문을 즉시 취소하세요.",
              ServiceCategory.DELIVERY: "결제를 완료하세요. 주문 완료 후 '주문내역'에서 조리 시작 전에 즉시 주문을 취소하세요.",
              ServiceCategory.MOBILITY: "호출을 완료하세요. 기사 배정 전이든 후든 즉시 '호출 취소'를 눌러 취소하세요.",
              ServiceCategory.TRAVEL: "무료 취소가 가능한 상품만 선택하세요. 결제를 완료한 후, '예약내역'에서 즉시 무료 취소하세요.",
              ServiceCategory.RESERVATION: "예약을 완료하세요. 예약 확인 후 '예약내역'에서 즉시 취소하세요.",
              ServiceCategory.GIFT: "선물하기를 완료하세요. 전송 후 상대방이 확인하기 전에 '선물내역'에서 즉시 취소하세요.",
          }
          
          suffix = safety_suffixes.get(intent.category, "")
          return f"{base_goal} {suffix}".strip()
  ```
- **Acceptance Criteria**:
  - shopping intent → goal에 "결제를 완료" + "즉시 취소" 접미사 포함
  - mobility intent → goal에 "호출을 완료" + "즉시 취소" 접미사 포함
- **QA Scenario**: 각 카테고리별 안전 접미사 포함 여부 테스트
- **Depends on**: Task 2.1

## Wave 4: Service Handlers (예상 90분)

### Task 4.1: Service Handler Base Class
- **Category**: `deep`
- **Skills**: `git-master`
- **What**: 모든 서비스 핸들러의 공통 인터페이스 정의
- **Files to create**:
  - `src/services/__init__.py`
  - `src/services/base.py`
- **Implementation guidance**:
  ```python
  from abc import ABC, abstractmethod
  from src.intent.schemas import ParsedIntent
  from src.agent.minitap_agent import MinitapAgentWrapper
  
  class ServiceHandler(ABC):
      def __init__(self, agent: MinitapAgentWrapper):
          self.agent = agent
      
      @abstractmethod
      def get_bundle_id(self) -> str:
          """해당 서비스의 iOS 앱 bundle ID"""
          pass
      
      @abstractmethod
      def build_goal(self, intent: ParsedIntent) -> str:
          """인텐트를 Minitap goal 문장으로 변환"""
          pass
      
      async def execute(self, intent: ParsedIntent) -> dict:
          """서비스 실행 — 공통 플로우"""
          goal = self.build_goal(intent)
          bundle_id = self.get_bundle_id()
          
          # Preflight: health check
          if not await self.agent.health_check():
              await self.agent.initialize()
          
          result = await self.agent.execute_task(
              goal=goal,
              bundle_id=bundle_id,
          )
          
          # Post-execution: 스크린샷 캡처
          screenshot_path = await self.agent.take_screenshot()
          result["screenshot"] = screenshot_path
          
          return result
  ```
- **Acceptance Criteria**:
  - ServiceHandler가 추상 클래스로 정의됨
  - execute() 메서드가 goal 생성 → Minitap 실행 → 스크린샷 캡처 플로우 구현
- **QA Scenario**: mock agent로 execute() 호출 시 올바른 순서로 메서드 호출 확인

### Task 4.2: Shopping + Delivery Handlers
- **Category**: `deep`
- **Skills**: `git-master`
- **What**: 쇼핑(쿠팡/네이버) + 배달(배민/쿠팡이츠) 핸들러 구현
- **Files to create**:
  - `src/services/shopping.py`
  - `src/services/delivery.py`
- **Implementation guidance for shopping.py**:
  ```python
  from src.services.base import ServiceHandler
  from src.intent.schemas import ParsedIntent
  from src.config import settings
  
  class CoupangHandler(ServiceHandler):
      def get_bundle_id(self) -> str:
          return settings.coupang_bundle_id
      
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
      def get_bundle_id(self) -> str:
          return settings.naver_bundle_id
      
      def build_goal(self, intent: ParsedIntent) -> str:
          entities = intent.entities
          product = entities.get("product", "상품")
          return (
              f"네이버 앱을 열고, 검색창에 '{product}'을(를) 검색하세요. "
              f"'쇼핑' 탭으로 이동하여 가격이 적절한 상품을 선택하고, "
              f"결제를 완료하세요. 주문 완료 후 '주문내역'에서 즉시 취소하세요."
          )
  ```
- **Implementation guidance for delivery.py**: 유사한 패턴으로 BaeminHandler, CoupangEatsHandler 구현. 배달은 주소 기반 검색 → 메뉴 선택 → 장바구니 담기 플로우.
- **Acceptance Criteria**:
  - CoupangHandler, NaverShoppingHandler, BaeminHandler, CoupangEatsHandler 클래스 존재
  - 각 핸들러의 build_goal()이 앱에 맞는 구체적 지시를 생성
  - 이전 주문 기반 재주문 로직 포함 (shopping)
- **QA Scenario**: `pytest tests/test_services.py::test_shopping_goal_generation` 통과
- **Depends on**: Task 4.1

### Task 4.3: Mobility + Travel + Reservation + Gift Handlers
- **Category**: `deep`
- **Skills**: `git-master`
- **What**: 나머지 4개 카테고리 핸들러 구현
- **Files to create**:
  - `src/services/mobility.py` — KakaoTHandler
  - `src/services/travel.py` — YanoljaHandler
  - `src/services/reservation.py` — CatchtableHandler, NaverReservationHandler
  - `src/services/gift.py` — KakaoGiftHandler
- **Critical implementation notes**:
  - **KakaoT**: goal에 "예약 후 즉시 취소" 포함. 시간/목적지 엔티티를 goal에 명시.
    ```python
    # mobility.py
    def build_goal(self, intent):
        dest = intent.entities.get("destination", "목적지")
        time = intent.entities.get("pickup_time", "")
        time_str = f"{time}에 " if time else ""
        return (
            f"카카오T 앱을 열고, {time_str}{dest}까지 택시를 호출해주세요. "
            f"예약이 완료되면, 바로 해당 예약을 취소해주세요."
        )
    ```
  - **Travel (야놀자/여기어때)**: goal에 "무료 취소 가능한 상품만" + "예약 후 취소" 포함.
  - **Reservation (캐치테이블)**: 시간/인원수를 goal에 명시. 예약 후 취소.
  - **Gift (카카오톡)**: "카카오톡 → 더보기 → 선물하기" 네비게이션 포함. 결제 직전 중단.
- **Acceptance Criteria**:
  - 모든 6개 카테고리에 최소 1개 핸들러 존재
  - 각 핸들러의 build_goal()이 서비스 특성에 맞는 안전 가드레일 포함
  - mobility: "취소" 키워드 포함
  - travel: "무료 취소" + "취소" 키워드 포함
- **QA Scenario**: `pytest tests/test_services.py` — 모든 핸들러 goal 생성 + 안전 키워드 테스트 통과
- **Depends on**: Task 4.1

## Wave 5: CLI Interface + Conversation (예상 45분)

### Task 5.1: Conversation State Manager
- **Category**: `deep`
- **Skills**: `git-master`
- **What**: 대화 상태 관리 — 멀티턴, 슬롯 필링, 세션 관리
- **Files to create**:
  - `src/state/__init__.py`
  - `src/state/conversation.py`
- **Implementation guidance**:
  ```python
  from dataclasses import dataclass, field
  from typing import Optional
  from datetime import datetime
  from src.intent.schemas import ParsedIntent
  
  @dataclass
  class ConversationSession:
      user_id: int  # Telegram user ID
      created_at: datetime = field(default_factory=datetime.now)
      history: list[dict] = field(default_factory=list)  # {"role": "user"|"assistant", "content": str}
      pending_intent: Optional[ParsedIntent] = None  # 명확화 대기 중인 인텐트
      last_result: Optional[dict] = None
  
  class ConversationManager:
      def __init__(self):
          self._sessions: dict[int, ConversationSession] = {}
      
      def get_session(self, user_id: int) -> ConversationSession:
          if user_id not in self._sessions:
              self._sessions[user_id] = ConversationSession(user_id=user_id)
          return self._sessions[user_id]
      
      def add_message(self, user_id: int, role: str, content: str):
          session = self.get_session(user_id)
          session.history.append({
              "role": role,
              "content": content,
              "timestamp": datetime.now().isoformat()
          })
          # Keep last 20 messages
          if len(session.history) > 20:
              session.history = session.history[-20:]
      
      def set_pending_intent(self, user_id: int, intent: ParsedIntent):
          session = self.get_session(user_id)
          session.pending_intent = intent
      
      def clear_pending(self, user_id: int):
          session = self.get_session(user_id)
          session.pending_intent = None
      
      def get_context_for_parser(self, user_id: int) -> dict:
          """파서에 전달할 대화 컨텍스트"""
          session = self.get_session(user_id)
          return {
              "history": [
                  {"role": msg["role"], "content": msg["content"]}
                  for msg in session.history[-5:]
              ]
          }
  ```
- **Acceptance Criteria**:
  - 새 사용자 → 새 세션 자동 생성
  - 메시지 추가 → 히스토리 업데이트
  - 히스토리 20개 제한 (오래된 것 삭제)
  - pending_intent 설정/해제 동작
- **QA Scenario**: `pytest tests/test_conversation.py` 통과
- **Depends on**: Task 2.1

### Task 5.2: CLI Interactive Interface (Phase 1 — MVP)
- **Category**: `deep`
- **Skills**: `git-master`
- **What**: 터미널 기반 대화형 인터페이스 — 먼저 CLI로 전체 파이프라인 검증
- **Files to create**:
  - `src/cli/__init__.py`
  - `src/cli/app.py`
- **Implementation guidance for app.py**:
  ```python
  import asyncio
  from src.intent.parser import IntentParser
  from src.router.router import ServiceRouter
  from src.agent.minitap_agent import MinitapAgentWrapper
  from src.state.conversation import ConversationManager
  from src.services.base import ServiceHandler
  
  class CLIApp:
      def __init__(self, parser: IntentParser, router: ServiceRouter,
                   agent: MinitapAgentWrapper, handlers: dict[str, ServiceHandler]):
          self.parser = parser
          self.router = router
          self.agent = agent
          self.handlers = handlers
          self.conversation = ConversationManager()
          self.user_id = 0  # CLI는 단일 사용자
      
      async def run(self):
          print("=" * 60)
          print("🔔 딸깍(DDalkkak) — 딸깍 한 번으로 주문/예약 완료")
          print("=" * 60)
          print("주문, 배달, 택시, 여행, 예약, 선물 — 뭐든 말씀해주세요.")
          print("종료: 'quit' 또는 'exit'\n")
          print("예시:")
          print("  • 샴푸 다 떨어졌다. 주문해줘")
          print("  • 오늘 저녁 혼자 먹을 거 추천해서 주문해줘")
          print("  • 내일 아침 7시에 공항 가는 택시 잡아줘")
          print("  • 이번 주말 제주도 숙소 예약해줘")
          print("  • 근처 맛집 예약해줘")
          print("  • 부모님 집으로 과일 선물 보내줘")
          print("-" * 60)
          
          while True:
              try:
                  user_input = input("\n💬 You: ").strip()
              except (EOFError, KeyboardInterrupt):
                  break
              
              if user_input.lower() in ("quit", "exit", "종료"):
                  print("👋 딸깍을 종료합니다.")
                  break
              if not user_input:
                  continue
              
              self.conversation.add_message(self.user_id, "user", user_input)
              ctx = self.conversation.get_context_for_parser(self.user_id)
              
              # 1. 인텐트 파싱
              print("🤔 분석 중...")
              try:
                  intent = await self.parser.parse(user_input, context=ctx)
              except Exception as e:
                  print(f"❌ 인텐트 파싱 실패: {e}")
                  continue
              
              # 2. 명확화 필요 시
              if intent.needs_clarification:
                  self.conversation.set_pending_intent(self.user_id, intent)
                  print(f"🤔 {intent.clarification_question}")
                  self.conversation.add_message(self.user_id, "assistant", intent.clarification_question)
                  continue
              
              # 3. 서비스 라우팅
              app_key, bundle_id, display_name = self.router.route(intent)
              print(f"📱 {display_name}에서 처리합니다...")
              print(f"   카테고리: {intent.category.value}")
              print(f"   액션: {intent.action.value}")
              print(f"   앱: {display_name} ({bundle_id})")
              
              # 4. Minitap 실행
              handler = self.handlers.get(app_key)
              if not handler:
                  print(f"❌ {display_name} 핸들러가 아직 구현되지 않았습니다.")
                  continue
              
              try:
                  result = await handler.execute(intent)
                  print(f"✅ {display_name}에서 처리 완료!")
                  if result.get("screenshot"):
                      print(f"📸 스크린샷: {result['screenshot']}")
                  if result.get("trace_path"):
                      print(f"📁 Trace: {result['trace_path']}")
                  self.conversation.add_message(self.user_id, "assistant", f"{display_name} 처리 완료")
              except Exception as e:
                  print(f"❌ 실행 중 오류: {e}")
  ```
- **Acceptance Criteria**:
  - `uv run python -m src.main` 실행 시 CLI 대화 인터페이스 시작
  - 자연어 입력 → 인텐트 파싱 → 라우팅 → Minitap 실행 → 결과 출력
  - 명확화 필요 시 질문 출력 후 재입력 대기
  - quit/exit/종료로 깔끔한 종료
- **QA Scenario**: CLI에서 6개 카테고리 각 1개 입력 → 올바른 라우팅 확인
- **Depends on**: Task 2.2, Task 2.3, Task 3.1, Task 5.1

### Task 5.3: Main Entry Point
- **Category**: `quick`
- **Skills**: `git-master`
- **What**: 애플리케이션 엔트리포인트 — 모든 컴포넌트 초기화 + CLI 시작
- **Files to create**:
  - `src/main.py`
- **Implementation guidance**:
  ```python
  import asyncio
  import logging
  from src.config import settings
  from src.agent.minitap_agent import MinitapAgentWrapper
  from src.intent.parser import IntentParser
  from src.router.router import ServiceRouter
  from src.cli.app import CLIApp
  from src.services.shopping import CoupangHandler, NaverShoppingHandler
  from src.services.delivery import BaeminHandler, CoupangEatsHandler
  from src.services.mobility import KakaoTHandler
  from src.services.travel import YanoljaHandler
  from src.services.reservation import CatchtableHandler, NaverReservationHandler
  from src.services.gift import KakaoGiftHandler
  
  logging.basicConfig(
      level=logging.INFO,
      format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
  )
  logger = logging.getLogger("ddalkkak")
  
  async def run():
      agent = MinitapAgentWrapper()
      parser = IntentParser()
      router = ServiceRouter()
      
      logger.info("Initializing Minitap agent...")
      ok = await agent.initialize()
      if not ok:
          logger.error("Minitap agent initialization failed!")
          raise RuntimeError("Failed to initialize Minitap agent")
      logger.info("Minitap agent initialized")
      
      handlers = {
          "coupang": CoupangHandler(agent),
          "naver_shopping": NaverShoppingHandler(agent),
          "baemin": BaeminHandler(agent),
          "coupang_eats": CoupangEatsHandler(agent),
          "kakaot": KakaoTHandler(agent),
          "yanolja": YanoljaHandler(agent),
          "catchtable": CatchtableHandler(agent),
          "naver_reservation": NaverReservationHandler(agent),
          "kakao_gift": KakaoGiftHandler(agent),
      }
      logger.info(f"Registered {len(handlers)} service handlers")
      
      app = CLIApp(parser=parser, router=router, agent=agent, handlers=handlers)
      await app.run()
      await agent.cleanup()
  
  def main():
      asyncio.run(run())
  
  if __name__ == "__main__":
      main()
  ```
- **Acceptance Criteria**:
  - `uv run python -m src.main` 실행 시:
    1. Minitap 에이전트 초기화 성공 로그
    2. 9개 서비스 핸들러 등록 로그
    3. CLI 대화 인터페이스 시작
  - quit/exit/Ctrl+C로 깔끔하게 종료 + agent cleanup
- **QA Scenario**: 실행 후 CLI에서 "샴푸 주문해줘" 입력 → 쿠팡 라우팅 확인
- **Depends on**: Task 5.2, Task 4.2, Task 4.3

## Wave 6: Integration + Polish (예상 45분)

### Task 6.1: Error Handling & Retry Logic
- **Category**: `deep`
- **Skills**: `git-master`
- **What**: 전체 파이프라인에 대한 에러 분류 + 재시도 + 회복 로직
- **What to implement**:
  - `src/agent/minitap_agent.py` 수정: execute_task에 retry decorator 추가
    - 최대 3회 재시도, exponential backoff (2s, 4s, 8s)
    - WDA 연결 실패 시 agent 재초기화 후 재시도
  - `src/intent/parser.py` 수정: Claude API 호출에 retry 추가
    - Rate limit (429) → 30초 대기 후 재시도
    - Timeout → 2회 재시도
  - `src/bot/handlers.py` 수정: 전체 핸들러에 try-except 강화
    - 사용자에게 친절한 에러 메시지 (한국어)
    - 에러 로깅 (traceback 포함)
- **Error taxonomy**:
  ```python
  class DDalkkakError(Exception): pass
  class MinitapConnectionError(DDalkkakError): pass
  class MinitapExecutionError(DDalkkakError): pass
  class IntentParsingError(DDalkkakError): pass
  class ServiceRoutingError(DDalkkakError): pass
  class ServiceNotAvailableError(DDalkkakError): pass
  ```
- **Acceptance Criteria**:
  - Minitap 연결 실패 → 3회 재시도 → 실패 시 사용자에게 "디바이스 연결 확인" 메시지
  - Claude API 실패 → 재시도 → 실패 시 사용자에게 "다시 시도해주세요" 메시지
  - 예상치 못한 에러 → 로그 기록 + 사용자에게 일반 에러 메시지
- **QA Scenario**: `pytest tests/` — 에러 시나리오 테스트 (mock으로 의도적 실패 유발)
- **Depends on**: Task 5.2, Task 3.1

### Task 6.2: Test Suite
- **Category**: `deep`
- **Skills**: `git-master`
- **What**: 단위 테스트 + 통합 테스트 + 스모크 테스트
- **Files to create/update**:
  - `tests/test_parser.py` — 인텐트 파싱 테스트 (mock Claude API)
  - `tests/test_router.py` — 라우팅 테스트
  - `tests/test_services.py` — 서비스 핸들러 goal 생성 테스트
  - `tests/test_agent.py` — Minitap 래퍼 테스트 (mock SDK)
  - `tests/test_conversation.py` — 대화 상태 관리 테스트
  - `tests/conftest.py` — 공통 fixture (mock agent, mock parser)
- **Test categories**:
  ```python
  # tests/test_parser.py
  @pytest.mark.parametrize("input,expected_category", [
      ("샴푸 다 떨어졌다. 주문해줘", "shopping"),
      ("오늘 저녁 혼자 먹을 거 추천해서 주문해줘", "delivery"),
      ("내일 아침 7시에 공항 가는 택시 잡아줘", "mobility"),
      ("이번 주말 제주도 숙소 예약해줘", "travel"),
      ("근처에서 지금 바로 먹을 수 있는 맛집 예약해줘", "reservation"),
      ("부모님 집으로 과일 선물 보내줘", "gift"),
  ])
  async def test_intent_categories(input, expected_category):
      # Mock Claude API response
      ...
  
  # tests/test_router.py
  def test_all_categories_routed():
      router = ServiceRouter()
      for category in ServiceCategory:
          intent = ParsedIntent(category=category, ...)
          app_key, bundle_id, name = router.route(intent)
          assert bundle_id  # not empty
  
  # tests/test_services.py
  def test_safety_guards_in_goals():
      """모든 핸들러의 goal에 안전 가드 포함 확인"""
      # shopping/delivery → "결제 버튼은 누르지 마세요"
      # mobility → "취소"
      # travel → "무료 취소"
      ...
  ```
- **Acceptance Criteria**:
  - `pytest tests/ -v` 전체 통과
  - 최소 20개 테스트 케이스
  - 각 카테고리별 최소 1개 테스트
  - mock 기반 (실제 API 호출 없이)
- **QA Scenario**: `pytest tests/ -v --tb=short` 전체 GREEN
- **Depends on**: Task 5.3

### Task 6.3: Demo Script + Documentation Finalize
- **Category**: `quick`
- **Skills**: `git-master`
- **What**: 데모 시나리오 스크립트 + README 최종 업데이트
- **Files to create/update**:
  - `scripts/demo.py` — 데모 시나리오 자동 실행 (Telegram 없이 직접 파이프라인 테스트)
    ```python
    # scripts/demo.py
    import asyncio
    from src.intent.parser import IntentParser
    from src.router.router import ServiceRouter
    from src.agent.minitap_agent import MinitapAgentWrapper
    
    DEMO_SCENARIOS = [
        "샴푸 다 떨어졌다. 주문해줘",
        "오늘 저녁 혼자 먹을 거 추천해서 주문해줘",
        "내일 아침 7시에 공항 가는 택시 잡아줘",
    ]
    
    async def run_demo():
        parser = IntentParser()
        router = ServiceRouter()
        agent = MinitapAgentWrapper()
        await agent.initialize()
        
        for scenario in DEMO_SCENARIOS:
            print(f"\n{'='*60}")
            print(f"📝 Input: {scenario}")
            intent = await parser.parse(scenario)
            print(f"🎯 Intent: {intent.category.value} / {intent.action.value}")
            app_key, bundle_id, name = router.route(intent)
            print(f"📱 Routing to: {name} ({bundle_id})")
            # Execute on device
            result = await agent.execute_task(
                goal=intent.minitap_goal,
                bundle_id=bundle_id,
            )
            print(f"✅ Result: {result}")
        
        await agent.cleanup()
    
    if __name__ == "__main__":
        asyncio.run(run_demo())
    ```
  - `README.md` 최종 업데이트:
    - 실행 방법, 데모 시나리오, 아키텍처, 서비스 목록
    - 트러블슈팅 가이드 (WDA 연결 실패, 앱 로그인 만료 등)
- **Acceptance Criteria**:
  - `python scripts/demo.py` 실행 가능 (Minitap 연결 시 실제 동작)
  - README.md에 데모 시나리오 3개 이상 문서화
  - 트러블슈팅 섹션 존재
- **QA Scenario**: 데모 스크립트 실행 → 3개 시나리오 순차 처리 확인
- **Depends on**: Task 5.3

## Wave 7: App-specific Test Scenario Verification (구현 완료 후)

> 이 Wave는 Wave 1-6 완료 후 실행됩니다.
> 각 앱별 5개 시나리오를 .md 파일로 작성하고, 실제 실행하여 검증합니다.
> **실패 시 Ralph loop를 재시작하여 해당 핸들러를 수정합니다.**

### Task 7.1: Test Scenario Files 생성
- **Category**: `deep`
- **Skills**: `git-master`
- **What**: 9개 앱 × 5개 시나리오 = 45개 테스트 시나리오를 별도 .md 파일로 작성
- **Files to create**:
  - `tests/scenarios/coupang.md` — 쿠팡 5개 시나리오
  - `tests/scenarios/naver_shopping.md` — 네이버쇼핑 5개 시나리오
  - `tests/scenarios/baemin.md` — 배달의민족 5개 시나리오
  - `tests/scenarios/coupang_eats.md` — 쿠팡이츠 5개 시나리오
  - `tests/scenarios/kakaot.md` — 카카오T 5개 시나리오
  - `tests/scenarios/yanolja.md` — 야놀자 5개 시나리오
  - `tests/scenarios/catchtable.md` — 캐치테이블 5개 시나리오
  - `tests/scenarios/naver_reservation.md` — 네이버예약 5개 시나리오
  - `tests/scenarios/kakao_gift.md` — 카카오톡 선물하기 5개 시나리오
- **시나리오 내용**: `.sisyphus/drafts/test-scenarios.md` 참조
- **각 시나리오 포맷**:
  ```markdown
  ### TC-{APP}-{NUM}: {시나리오 이름}
  - **입력**: 사용자 자연어
  - **기대 인텐트**: category / action / entities
  - **Minitap Goal**: 구체적 앱 조작 지시
  - **성공 기준**: 화면 확인 사항
  - **안전 가드**: 제한 사항
  - **결과**: PASS / PARTIAL / FAIL
  - **스크린샷**: (실행 후 기록)
  - **실패 원인**: (실패 시 기록)
  ```
- **Acceptance Criteria**: 9개 .md 파일 각각 5개 시나리오 포함
- **Depends on**: Task 6.3

### Task 7.2: Scenario Runner Script
- **Category**: `deep`
- **Skills**: `git-master`
- **What**: .md 시나리오를 파싱하여 자동 실행하는 스크립트
- **Files to create**:
  - `scripts/run_scenarios.py`
- **Implementation guidance**:
  ```python
  # scripts/run_scenarios.py
  # 1. tests/scenarios/*.md 파일 로드
  # 2. 각 시나리오의 "입력" 추출
  # 3. 파이프라인 실행: parse → route → execute
  # 4. 결과를 .md 파일에 기록 (PASS/PARTIAL/FAIL)
  # 5. 스크린샷 경로 기록
  # 6. 최종 리포트 출력 (N/45 PASS)
  ```
- **Usage**: `uv run python scripts/run_scenarios.py --app coupang` (특정 앱) 또는 `--all`
- **Acceptance Criteria**:
  - 시나리오 실행 후 .md 파일에 결과 자동 기록
  - 최종 리포트에 전체 pass rate 표시
- **Depends on**: Task 7.1

### Task 7.3: Scenario Verification + Fix Loop
- **Category**: `deep`
- **Skills**: `git-master`
- **What**: 시나리오 실행 결과 검증 + 실패 시 핸들러 수정
- **실행 방법**:
  1. `uv run python scripts/run_scenarios.py --all` 실행
  2. FAIL인 시나리오 확인
  3. 해당 서비스 핸들러의 `build_goal()` 수정 (goal 문장을 더 구체적으로)
  4. 필요시 `max_steps` 조정, task 분할
  5. 재실행하여 PASS 확인
  6. **모든 시나리오 PASS까지 반복** (또는 PARTIAL로 수용 가능한 경우 기록)
- **Acceptance Criteria**:
  - 전체 45개 시나리오 중 최소 70% PASS (32/45)
  - 각 앱별 최소 3/5 PASS
  - FAIL인 경우 실패 원인과 개선 방향 기록
- **Depends on**: Task 7.2

---

## Wave 8: KakaoTalk Integration (Optional — Phase 1 검증 완료 후)

> ⚠️ CLI에서 전체 파이프라인이 검증된 후에만 진행.
> 시간 부족 시 스킵 가능.

### Task 8.1: KakaoTalk Chatbot Integration
- **Category**: `deep`
- **Skills**: `git-master`
- **What**: 카카오톡 챗봇 연동 — 카카오 비즈니스 채널 + 챗봇 API
- **Files to create**:
  - `src/kakao/__init__.py`
  - `src/kakao/chatbot.py` — 카카오 i 오픈빌더 또는 카카오톡 채널 API 연동
- **Prerequisites**: 카카오 비즈니스 계정 + 채널 개설 + 봇 설정 (사전 작업 필요)
- **Acceptance Criteria**: 카카오톡에서 메시지 수신 → 파이프라인 실행 → 결과 반환
- **Depends on**: Task 5.2 (CLI 검증 완료), Task 7.3 (시나리오 검증 완료)

---

## Final Verification Wave

> ⚠️ 이 Wave는 모든 이전 Wave 완료 후 실행됩니다.
> **Ralph는 이 단계에서 반드시 사용자에게 확인을 구해야 합니다.**

### FV-1: End-to-End Smoke Test
- CLI 시작 → 테스트 메시지 입력 → 인텐트 파싱 → 서비스 라우팅 → Minitap 에이전트 실행 확인
- 최소 2개 카테고리에서 happy path 성공

### FV-2: Error Scenario Test
- 잘못된 입력 → 적절한 에러 메시지 반환
- Minitap 연결 실패 → 사용자에게 알림
- 인텐트 모호 → 명확화 질문 생성

### FV-3: Demo Recording Readiness
- 데모 시나리오 스크립트 존재
- Telegram 대화 + iPhone 화면 동시 캡처 가능

### Completion Criteria
```
Ralph는 아래 모든 조건 충족 시에만 작업 완료로 표시:
□ uv run ruff check . 에러 없음
□ uv run pytest 전체 통과
□ CLI가 정상 기동되고 자연어 입력에 응답
□ 최소 1개 서비스에서 Minitap 에이전트가 iPhone 앱을 실제로 조작
□ 앱별 테스트 시나리오 45개 중 최소 70% PASS (32/45)
□ README.md에 아키텍처, 실행 방법, 데모 시나리오 문서화 완료
□ 사용자에게 "okay" 확인을 받음 (자동 완료 금지)
```

---

## Guardrails & Constraints

1. **실제 결제 + 즉시 취소**: 결제/예약을 실제로 완료한 뒤, 성공 확인 후 즉시 취소한다. 장바구니에서 멈추지 않는다.
2. **즉시 취소 가능한 건만**: 테스트/검증 시에는 반드시 즉시 취소 가능한 상품/서비스만 대상으로 한다.
   - 쇼핑: 주문 후 → '주문 취소' (배송 전 취소)
   - 배달: 주문 후 → '주문 취소' (조리 시작 전 취소)
   - 모빌리티: 호출 후 → 즉시 취소 (5분 쿨다운 인지)
   - 여행: 무료 취소 가능 상품만 → 예약 후 취소
   - 예약: 예약 후 → 즉시 취소
   - 선물: 선물 전송 후 → 수신자 확인 전 취소
3. **세션 보존**: 앱 로그인 세션이 만료되지 않도록 iPhone 자동 잠금 = "안 함" 유지.
4. **PII 보호**: 로그에 개인정보(전화번호, 주소, 카드번호) 노출 금지. trace 파일은 .gitignore에 포함.
5. **Minitap 안정성**: 각 task 실행 후 agent.clean() 호출. 실패 시 재초기화.
6. **인텐트 모호성**: 파서 confidence가 낮으면 실행하지 말고 명확화 질문 생성.
7. **Rate Limiting**: Minitap task 간 최소 5초 간격. Claude API 호출 간 최소 1초 간격.
8. **시크릿 관리**: .env는 절대 git commit 하지 않음. .env.example만 커밋.

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| WDA 연결 실패 | Medium | Critical | 사전 작업에서 테스트 필수. 실패 시 agent.init() 재시도 로직. |
| 앱 UI 변경 | Low | High | Minitap이 AI 기반이므로 UI 변경에 상대적 내성. goal을 구체적으로 작성. |
| Claude API rate limit | Low | Medium | 인텐트 파싱 결과 캐싱. 동일 입력 재요청 방지. |
| iPhone 배터리 방전 | Medium | Critical | USB 연결 = 충전 중. 하지만 5시간 연속 사용 시 발열 가능 → 방열 고려. |
| Telegram bot 토큰 노출 | Low | High | .env에만 저장, .gitignore 필수. |
| 인텐트 파싱 실패 (한국어) | Low | Medium | Claude는 한국어 성능 우수. fallback으로 원문 그대로 Minitap goal에 전달. |
| Minitap 400 step 초과 | Medium | Medium | 복잡한 플로우는 여러 task로 분할. max_steps 조정 가능. |

---

## Success Criteria

### Minimum Viable Prototype (MVP) — 5시간 내 필수 달성
1. ✅ CLI가 한국어 자연어 입력을 받음
2. ✅ Claude API가 인텐트를 정확히 파싱 (6개 카테고리)
3. ✅ 서비스 라우터가 올바른 앱으로 라우팅
4. ✅ Minitap이 실제 iPhone에서 최소 1개 앱을 자동 조작
5. ✅ End-to-end 플로우 비디오 녹화 가능

### Stretch Goals (시간 여유 시)
- 모든 6개 카테고리 동작
- 다중 서비스 가격 비교 (예: 배민 vs 쿠팡이츠)
- 이전 주문 기반 추천
- 대화 히스토리 기반 슬롯 필링
- KakaoTalk 챗봇 연동 (Phase 2)
