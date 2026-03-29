from __future__ import annotations

import asyncio
import base64
import contextlib
import logging
import subprocess
import time
from datetime import datetime
from pathlib import Path

import anthropic
from appium import webdriver
from appium.options.ios import XCUITestOptions

from src.config import settings

logger = logging.getLogger("ddalkkak.agent")

ANALYZE_PROMPT = """당신은 iOS 앱 자동화 에이전트입니다. 스크린샷을 분석하고 다음 액션을 결정합니다.

## 현재 목표
{goal}

## 지금까지 수행한 액션
{history}

## 규칙
1. 스크린샷을 보고 현재 상태를 정확히 파악하세요
2. 목표를 달성하기 위한 **다음 1개 액션만** 결정하세요
3. 목표가 달성되었으면 status를 "completed"로 설정하세요

## 응답 형식 (JSON)
반드시 아래 JSON 형식으로만 응답하세요:
{{"action": "tap", "x": 100, "y": 200, "description": "검색 버튼 탭"}}
{{"action": "type", "text": "맛집", "description": "검색어 입력"}}
{{"action": "swipe", "direction": "up", "description": "아래로 스크롤"}}
{{"action": "back", "description": "뒤로 가기"}}
{{"action": "wait", "seconds": 2, "description": "로딩 대기"}}
{{"action": "completed", "status": "completed", "description": "목표 달성 완료"}}
{{"action": "failed", "status": "failed", "description": "목표 달성 불가 - 이유 설명"}}
"""


def _start_appium_server() -> subprocess.Popen | None:
    try:
        import urllib.request

        urllib.request.urlopen(f"{settings.appium_host}/status", timeout=3)
        logger.info("Appium server already running")
        return None
    except Exception:
        pass
    logger.info("Starting Appium server...")
    proc = subprocess.Popen(
        ["appium", "--address", "127.0.0.1", "--port", "4723", "--relaxed-security"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(15):
        time.sleep(1)
        try:
            import urllib.request

            urllib.request.urlopen(f"{settings.appium_host}/status", timeout=2)
            logger.info("Appium server started (PID %d)", proc.pid)
            return proc
        except Exception:
            continue
    logger.error("Appium server failed to start within 15s")
    proc.kill()
    return None


class AppiumAgent:
    def __init__(self) -> None:
        self.driver: webdriver.Remote | None = None
        self._appium_proc: subprocess.Popen | None = None
        self._initialized = False
        self._claude = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    async def initialize(self) -> bool:
        if self._initialized:
            return True
        self._appium_proc = await asyncio.to_thread(_start_appium_server)
        opts = XCUITestOptions()
        opts.platform_name = "iOS"
        opts.automation_name = "XCUITest"
        opts.udid = settings.device_udid
        opts.device_name = "iPhone"
        opts.no_reset = True
        opts.set_capability("bundleId", "com.apple.springboard")
        opts.set_capability("newCommandTimeout", 300)
        opts.set_capability("wdaStartupRetries", 4)
        opts.set_capability("wdaStartupRetryInterval", 20000)
        opts.set_capability("wdaLocalPort", 8100)
        opts.set_capability("useNewWDA", False)
        opts.set_capability("showXcodeLog", False)
        try:
            self.driver = await asyncio.to_thread(webdriver.Remote, settings.appium_host, options=opts)
            self._initialized = True
            logger.info("Appium driver connected to %s", settings.device_udid)
            return True
        except Exception as e:
            logger.error("Appium driver init failed: %s", e)
            return False

    async def execute_task(
        self,
        goal: str,
        bundle_id: str,
        max_steps: int | None = None,
        trace_path: str | None = None,
        retries: int = 1,
    ) -> dict:
        if not self._initialized:
            await self.initialize()

        max_steps = max_steps or settings.appium_max_steps
        trace_dir = Path(trace_path or f"traces/{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        trace_dir.mkdir(parents=True, exist_ok=True)

        await asyncio.to_thread(self.driver.activate_app, bundle_id)
        await asyncio.sleep(2)
        logger.info("Activated app %s", bundle_id)

        history: list[str] = []
        for step in range(1, max_steps + 1):
            screenshot_b64 = await asyncio.to_thread(self.driver.get_screenshot_as_base64)
            img_path = trace_dir / f"step_{step:03d}.png"
            img_path.write_bytes(base64.b64decode(screenshot_b64))

            action = await self._ask_claude(goal, screenshot_b64, history)
            logger.info("Step %d/%d: %s", step, max_steps, action.get("description", ""))
            history.append(f"Step {step}: {action.get('description', '')}")

            if action.get("action") == "completed":
                return {"success": True, "result": action.get("description", ""), "trace_path": str(trace_dir)}
            if action.get("action") == "failed":
                return {"success": False, "error": action.get("description", ""), "trace_path": str(trace_dir)}

            await self._execute_action(action)
            await asyncio.sleep(settings.appium_step_interval)

        return {"success": False, "error": f"Max steps ({max_steps}) reached", "trace_path": str(trace_dir)}

    async def _ask_claude(self, goal: str, screenshot_b64: str, history: list[str]) -> dict:
        import json

        history_text = "\n".join(history[-10:]) if history else "(아직 없음)"
        prompt = ANALYZE_PROMPT.format(goal=goal, history=history_text)

        response = await asyncio.to_thread(
            self._claude.messages.create,
            model="claude-sonnet-4-20250514",
            max_tokens=512,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {"type": "base64", "media_type": "image/png", "data": screenshot_b64},
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        )
        text = response.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(text)

    async def _execute_action(self, action: dict) -> None:
        act = action.get("action", "")
        if act == "tap":
            x, y = action["x"], action["y"]
            await asyncio.to_thread(self.driver.tap, [(x, y)])
        elif act == "type":
            active = await asyncio.to_thread(lambda: self.driver.switch_to.active_element)
            await asyncio.to_thread(active.send_keys, action["text"])
        elif act == "swipe":
            size = await asyncio.to_thread(lambda: self.driver.get_window_size())
            w, h = size["width"], size["height"]
            direction = action.get("direction", "up")
            if direction == "up":
                await asyncio.to_thread(self.driver.swipe, w // 2, h * 3 // 4, w // 2, h // 4, 500)
            elif direction == "down":
                await asyncio.to_thread(self.driver.swipe, w // 2, h // 4, w // 2, h * 3 // 4, 500)
        elif act == "back":
            await asyncio.to_thread(self.driver.back)
        elif act == "wait":
            await asyncio.sleep(action.get("seconds", 2))

    async def take_screenshot(self) -> str | None:
        if not self._initialized:
            return None
        try:
            b64 = await asyncio.to_thread(self.driver.get_screenshot_as_base64)
            path = f"screenshots/{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_bytes(base64.b64decode(b64))
            return path
        except Exception as e:
            logger.warning("Screenshot failed: %s", e)
            return None

    async def cleanup(self) -> None:
        if self.driver:
            with contextlib.suppress(Exception):
                await asyncio.to_thread(self.driver.quit)
            self.driver = None
        if self._appium_proc:
            self._appium_proc.kill()
            self._appium_proc = None
        self._initialized = False

    async def health_check(self) -> bool:
        if not self._initialized or not self.driver:
            return False
        try:
            await asyncio.to_thread(self.driver.get_screenshot_as_base64)
            return True
        except Exception:
            return False
