from __future__ import annotations

from src.intent.schemas import ParsedIntent, ServiceAction, ServiceCategory
from src.state.conversation import ConversationManager


class TestConversationManager:
    def test_new_session_created(self) -> None:
        mgr = ConversationManager()
        session = mgr.get_session(1)
        assert session.user_id == 1
        assert session.history == []

    def test_add_message(self) -> None:
        mgr = ConversationManager()
        mgr.add_message(1, "user", "샴푸 주문해줘")
        session = mgr.get_session(1)
        assert len(session.history) == 1
        assert session.history[0]["role"] == "user"
        assert session.history[0]["content"] == "샴푸 주문해줘"

    def test_history_limit(self) -> None:
        mgr = ConversationManager()
        for i in range(25):
            mgr.add_message(1, "user", f"msg {i}")
        session = mgr.get_session(1)
        assert len(session.history) == 20

    def test_pending_intent(self) -> None:
        mgr = ConversationManager()
        intent = ParsedIntent(
            category=ServiceCategory.SHOPPING,
            action=ServiceAction.ORDER,
            entities={},
            minitap_goal="test",
            needs_clarification=True,
            clarification_question="어떤 브랜드를 원하시나요?",
        )
        mgr.set_pending_intent(1, intent)
        session = mgr.get_session(1)
        assert session.pending_intent is not None
        assert session.pending_intent.needs_clarification is True

        mgr.clear_pending(1)
        session = mgr.get_session(1)
        assert session.pending_intent is None

    def test_context_for_parser(self) -> None:
        mgr = ConversationManager()
        mgr.add_message(1, "user", "msg1")
        mgr.add_message(1, "assistant", "resp1")
        mgr.add_message(1, "user", "msg2")
        ctx = mgr.get_context_for_parser(1)
        assert len(ctx["history"]) == 3
        assert ctx["history"][0]["role"] == "user"
