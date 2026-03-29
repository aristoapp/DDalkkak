import unittest
from importlib import import_module

IntentParser = import_module("src.intent.parser").IntentParser
ParsedIntent = import_module("src.intent.schemas").ParsedIntent
ServiceCategory = import_module("src.intent.schemas").ServiceCategory


class _FakeToolUseBlock:
    type = "tool_use"
    name = "parse_intent"

    def __init__(self, tool_input: dict):
        self.input = tool_input


class _FakeResponse:
    def __init__(self, blocks: list[object]):
        self.content = blocks


class _FakeMessages:
    def __init__(self, response: _FakeResponse):
        self._response = response

    def create(self, **_: dict) -> _FakeResponse:
        return self._response


class _FakeClient:
    def __init__(self, response: _FakeResponse):
        self.messages = _FakeMessages(response)


class TestIntentParser(unittest.IsolatedAsyncioTestCase):
    def test_import_surface(self) -> None:
        self.assertIsNotNone(ParsedIntent)
        self.assertEqual(ServiceCategory.SHOPPING.value, "shopping")

    async def test_parser_parses_with_tool_use_response(self) -> None:
        response = _FakeResponse(
            [
                _FakeToolUseBlock(
                    {
                        "category": "shopping",
                        "action": "order",
                        "entities": {"product": "샴푸"},
                        "app_preference": "coupang",
                        "app_target": None,
                        "minitap_goal": "쿠팡에서 샴푸를 주문하세요.",
                        "needs_clarification": False,
                        "clarification_question": None,
                        "confidence": 0.92,
                    }
                )
            ]
        )
        parser = IntentParser(client=_FakeClient(response))

        intent = await parser.parse("샴푸 다 떨어졌다. 주문해줘")

        self.assertIsInstance(intent, ParsedIntent)
        self.assertEqual(intent.category, ServiceCategory.SHOPPING)
        self.assertEqual(intent.action.value, "order")
        self.assertIsInstance(intent.model_dump(mode="json"), dict)

    async def test_parser_fallback_is_json_serializable(self) -> None:
        parser = IntentParser(client=None, api_key=None)

        intent = await parser.parse("내일 아침 7시에 공항 가는 택시 잡아줘")

        self.assertIsInstance(intent, ParsedIntent)
        self.assertEqual(intent.category.value, "mobility")
        self.assertIsInstance(intent.model_dump(mode="json"), dict)
