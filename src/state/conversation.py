from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from src.intent.schemas import ParsedIntent


@dataclass
class ConversationSession:
    user_id: int
    created_at: datetime = field(default_factory=datetime.now)
    history: list[dict] = field(default_factory=list)
    pending_intent: ParsedIntent | None = None
    last_result: dict | None = None


class ConversationManager:
    def __init__(self) -> None:
        self._sessions: dict[int, ConversationSession] = {}

    def get_session(self, user_id: int) -> ConversationSession:
        if user_id not in self._sessions:
            self._sessions[user_id] = ConversationSession(user_id=user_id)
        return self._sessions[user_id]

    def add_message(self, user_id: int, role: str, content: str) -> None:
        session = self.get_session(user_id)
        session.history.append(
            {
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat(),
            }
        )
        if len(session.history) > 20:
            session.history = session.history[-20:]

    def set_pending_intent(self, user_id: int, intent: ParsedIntent) -> None:
        session = self.get_session(user_id)
        session.pending_intent = intent

    def clear_pending(self, user_id: int) -> None:
        session = self.get_session(user_id)
        session.pending_intent = None

    def get_context_for_parser(self, user_id: int) -> dict:
        session = self.get_session(user_id)
        return {"history": [{"role": msg["role"], "content": msg["content"]} for msg in session.history[-5:]]}
