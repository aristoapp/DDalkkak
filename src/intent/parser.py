from __future__ import annotations

from importlib import import_module
from typing import Any, cast

from src.memory import user_memory

from .schemas import ParsedIntent

_anthropic = import_module("anthropic")
_prompts = import_module("src.intent.prompts")
SYSTEM_PROMPT = _prompts.SYSTEM_PROMPT
PARSE_INTENT_TOOL = _prompts.PARSE_INTENT_TOOL


class IntentParser:
    def __init__(self, client: Any | None = None, api_key: str | None = None):
        if client is not None:
            self.client = client
            return

        if api_key is None:
            try:
                from src.config import settings

                api_key = settings.anthropic_api_key
            except Exception:
                api_key = None

        self.client = _anthropic.Anthropic(api_key=api_key) if api_key else None

    async def parse(self, user_message: str, context: dict | None = None) -> ParsedIntent:
        """Convert natural language to a ParsedIntent using Claude via tool_use"""
        messages = []
        if context and context.get("history"):
            for msg in context["history"][-5:]:
                messages.append(msg)
        messages.append({"role": "user", "content": user_message})

        if self.client is not None:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=SYSTEM_PROMPT + user_memory.get_profile_prompt(),
                tools=cast(Any, [PARSE_INTENT_TOOL]),
                messages=messages,
            )

            for block in response.content:
                if block.type == "tool_use" and block.name == "parse_intent":
                    return ParsedIntent(**block.input)

        return self._fallback_parse(user_message)

    def _fallback_parse(self, user_message: str) -> ParsedIntent:
        message = user_message.strip()

        category = "shopping"
        action = "order"

        if any(keyword in message for keyword in ("배달", "먹", "메뉴", "저녁", "점심")):
            category = "delivery"
            action = "recommend" if "추천" in message else "order"
        elif any(keyword in message for keyword in ("택시", "카카오t", "카카오택시", "공항")):
            category = "mobility"
            action = "book"
        elif any(keyword in message for keyword in ("숙소", "호텔", "펜션", "여행")):
            category = "travel"
            action = "book"
        elif any(keyword in message for keyword in ("예약", "식당", "맛집")):
            category = "reservation"
            action = "reserve"
        elif any(keyword in message for keyword in ("선물", "보내")):
            category = "gift"
            action = "order"

        return ParsedIntent(
            category=category,
            action=action,
            entities={"raw_text": message},
            app_preference=None,
            app_target=None,
            minitap_goal=f"사용자 요청을 수행하세요: {message}",
            needs_clarification=False,
            clarification_question=None,
            confidence=0.4,
        )
