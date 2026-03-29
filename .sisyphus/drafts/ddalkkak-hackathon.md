# DDalkkak Hackathon Plan - Draft

## Project Summary
- **Name**: DDalkkak (딸깍) — "One click to get things done"
- **Goal**: Natural language → intent parsing → Korean local service routing → transaction completion
- **Type**: Greenfield project (repo is empty except README.md)
- **Execution**: Ralph loop 5h unattended → must produce working prototype

## Exploration Findings

### Codebase Status
- EMPTY. Only README.md exists. Full greenfield build.

### Tech Stack Decision
- **Language**: Python (forced by Minitap SDK + browser-use)
- **Intent Parsing**: LLM function calling (Claude/OpenAI)
- **Browser Automation**: browser-use (AI-powered Playwright wrapper) or raw Playwright
- **Mobile Automation**: Minitap Mobile Use SDK (physical iOS via WDA)
- **Architecture**: Simple intent router, NOT MCP

### Service Difficulty Assessment
| Service | Difficulty | Automation Method |
|---------|-----------|-------------------|
| Naver Shopping | Medium | Browser (Playwright) |
| Naver Reservation | Medium-High | Browser |
| Kakao Gift | Medium | Browser |
| Yanolja/Yeogi-eottae | High | Browser |
| Catchtable | High | Browser |
| Coupang | VERY HIGH (Akamai) | Browser (low success) |
| Coupang Eats | High | Mobile (Minitap) |
| Baedal Minjok | High | Mobile (Minitap) |
| KakaoT | High | Mobile (Minitap) |

### Minitap Physical iOS Requirements
- macOS + Xcode + Xcode CLI Tools
- Python 3.12+
- Node.js + npm (for Appium)
- Apple Developer account (free OK)
- Physical iPhone via USB
- WDA one-time setup: install Appium → xcuitest driver → code sign → trust certificate

### Key Constraints
- Korean payment 2FA: Cannot be fully automated
- Session persistence: Must pre-authenticate and save sessions
- Coupang bot detection: Nearly impossible without specialized services
- Device must be unlocked for WDA initial setup

## Interview Questions (Pending)
1. Ralph loop scope — what should 5h produce?
2. Hardware readiness (Mac + iPhone)
3. Account/credential readiness
4. Service priorities
5. Demo format / judging criteria

## KEY PIVOT: ALL-MOBILE ARCHITECTURE
User decision: "브라우저 연동은 없애고 네이버/카카오/야놀자도 모바일(minitap)으로 연결"
→ REMOVE all browser automation
→ ALL services via Minitap physical iOS automation
→ This means: one unified automation layer (Minitap Agent only)

### Revised Architecture
```
User (자연어) → Intent Parser (LLM) → Service Router → Minitap Agent → Physical iPhone
                                                          ↓
                                            Target App (쿠팡/배민/카카오T/네이버/야놀자/캐치테이블 etc.)
```

### iPhone App Requirements (ALL must be pre-installed + pre-logged-in)
- 쇼핑: 쿠팡, 네이버쇼핑
- 배달: 쿠팡이츠, 배달의민족
- 모빌리티: 카카오T
- 여행: 야놀자, 여기어때
- 예약: 캐치테이블, 네이버 예약
- 선물: 카카오톡 (선물하기)

## Decisions Made
- [x] Python as primary language
- [x] LLM function calling for intent parsing
- [x] Skip MCP, use simple router pattern
- [x] ALL-MOBILE via Minitap (no browser automation)
- [x] Hardware ready (Mac + iPhone + USB + Xcode + Apple Dev)
- [x] Service accounts available
- [x] Demo: video, live if possible
- [ ] browser-use role clarification (may be moot with all-mobile)
- [ ] Which LLM (Claude vs OpenAI)
- [ ] User interface format (CLI/Web/Mobile)
- [ ] Ralph loop boundary (pre-work vs loop work)

## Pre-Work Required (Before Ralph Loop)
### MUST do manually:
1. WDA setup on physical iPhone
2. Login to all Korean services, save sessions/cookies
3. Set up .env with API keys (LLM, Minitap if using platform)
4. Install all dependencies (Python 3.12, Appium, npm packages)
5. Verify Minitap basic connectivity (trivial test script)
6. Verify browser-use basic connectivity (trivial test)

### Ralph loop will build:
- TBD based on interview answers
