from __future__ import annotations

from src.agent.droid_agent import DroidRunAgent
from src.intent.parser import IntentParser
from src.router.router import ServiceRouter
from src.services.base import ServiceHandler
from src.state.conversation import ConversationManager


class CLIApp:
    def __init__(
        self,
        parser: IntentParser,
        router: ServiceRouter,
        agent: DroidRunAgent,
        handlers: dict[str, ServiceHandler],
    ) -> None:
        self.parser = parser
        self.router = router
        self.agent = agent
        self.handlers = handlers
        self.conversation = ConversationManager()
        self.user_id = 0

    async def run(self) -> None:
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

            print("🤔 분석 중...")
            try:
                intent = await self.parser.parse(user_input, context=ctx)
            except Exception as e:
                print(f"❌ 인텐트 파싱 실패: {e}")
                continue

            if intent.needs_clarification:
                self.conversation.set_pending_intent(self.user_id, intent)
                print(f"🤔 {intent.clarification_question}")
                self.conversation.add_message(self.user_id, "assistant", intent.clarification_question or "")
                continue

            app_key, package_name, display_name = self.router.route(intent)
            print(f"📱 {display_name}에서 처리합니다...")
            print(f"   카테고리: {intent.category.value}")
            print(f"   액션: {intent.action.value}")
            print(f"   앱: {display_name} ({package_name})")

            handler = self.handlers.get(app_key)
            if not handler:
                print(f"❌ {display_name} 핸들러가 아직 구현되지 않았습니다.")
                continue

            try:
                result = await handler.execute(intent)
                if result.get("success"):
                    print(f"✅ {display_name}에서 처리 완료!")
                    if result.get("screenshot"):
                        print(f"📸 스크린샷: {result['screenshot']}")
                    if result.get("trace_path"):
                        print(f"📁 Trace: {result['trace_path']}")
                    self.conversation.add_message(self.user_id, "assistant", f"{display_name} 처리 완료")
                else:
                    print(f"⚠️ {display_name} 실행 실패: {result.get('error', '알 수 없는 오류')}")
                    if result.get("trace_path"):
                        print(f"📁 Trace: {result['trace_path']}")
            except Exception as e:
                print(f"❌ 실행 중 오류: {e}")
