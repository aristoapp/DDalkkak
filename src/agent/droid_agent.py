from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from pathlib import Path

from droidrun import (
    AgentConfig,
    DeviceConfig,
    DroidConfig,
    ExecutorConfig,
    FastAgentConfig,
    LoggingConfig,
    ManagerConfig,
)
from droidrun import (
    DroidAgent as DroidRunSdkAgent,
)
from droidrun.tools import AndroidDriver
from llama_index.llms.anthropic import Anthropic

from src.config import settings

logger = logging.getLogger("ddalkkak.agent")


def _build_droid_config(max_steps: int | None = None) -> DroidConfig:
    max_s = max_steps if max_steps is not None else settings.max_steps
    agent = AgentConfig(
        max_steps=max_s,
        reasoning=settings.reasoning_enabled,
        fast_agent=FastAgentConfig(vision=settings.vision_enabled),
        manager=ManagerConfig(vision=settings.vision_enabled),
        executor=ExecutorConfig(vision=settings.vision_enabled),
    )
    device = DeviceConfig(
        serial=settings.device_serial,
        use_tcp=settings.device_use_tcp,
        platform="android",
        auto_setup=False,
    )
    logging_cfg = LoggingConfig(
        save_trajectory=settings.save_trajectory,
        trajectory_path=settings.trajectory_path,
    )
    return DroidConfig(agent=agent, device=device, logging=logging_cfg)


def _build_llms() -> dict[str, Anthropic]:
    """One Anthropic LLM instance per role (Droidrun merges / validates keys)."""
    common = {
        "model": settings.droidrun_anthropic_model,
        "api_key": settings.anthropic_api_key,
        "temperature": 0.2,
        "max_tokens": 8192,
    }
    llm = Anthropic(**common)
    if settings.reasoning_enabled:
        return {
            "manager": llm,
            "executor": llm,
            "app_opener": llm,
        }
    return {
        "fast_agent": llm,
        "app_opener": llm,
    }


class DroidRunAgent:
    """Android automation via Droidrun Portal + DroidAgent (replaces Appium + XCUITest)."""

    def __init__(self) -> None:
        self._driver: AndroidDriver | None = None
        self._initialized = False

    async def initialize(self) -> bool:
        if self._initialized:
            return True
        try:
            self._driver = AndroidDriver(
                serial=settings.device_serial,
                use_tcp=settings.device_use_tcp,
            )
            await self._driver.connect()
            self._initialized = True
            logger.info("Droidrun AndroidDriver connected to %s", settings.device_serial)
            return True
        except Exception as e:
            logger.error("Droidrun driver init failed: %s", e)
            self._driver = None
            self._initialized = False
            return False

    async def execute_task(
        self,
        goal: str,
        package_name: str,
        max_steps: int | None = None,
        trace_path: str | None = None,
        retries: int = 1,
        **_kwargs: object,
    ) -> dict:
        _ = retries  # reserved for future retry loop (Appium API compat)
        if not self._initialized or not self._driver:
            await self.initialize()
        if not self._driver:
            return {"success": False, "error": "Driver not initialized", "trace_path": None}

        await self._driver.start_app(package_name)
        await asyncio.sleep(2)
        logger.info("Started app %s", package_name)

        config = _build_droid_config(max_steps=max_steps)
        if trace_path:
            config.logging.trajectory_path = str(Path(trace_path).parent)
        llms = _build_llms()

        agent = DroidRunSdkAgent(
            goal=goal,
            config=config,
            llms=llms,
            driver=self._driver,
        )
        try:
            handler = agent.run()
            async for _ in handler.stream_events():
                pass
            result = await handler
        except Exception as e:
            logger.exception("DroidAgent run failed: %s", e)
            return {"success": False, "error": str(e), "trace_path": config.logging.trajectory_path}

        trace_dir = trace_path or f"{config.logging.trajectory_path}/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        out: dict = {
            "success": bool(result.success),
            "trace_path": trace_dir,
        }
        if result.success:
            out["result"] = result.reason
        else:
            out["error"] = result.reason
        return out

    async def take_screenshot(self) -> str | None:
        if not self._initialized or not self._driver:
            return None
        try:
            png = await self._driver.screenshot()
            path = f"screenshots/{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_bytes(png)
            return path
        except Exception as e:
            logger.warning("Screenshot failed: %s", e)
            return None

    async def cleanup(self) -> None:
        self._driver = None
        self._initialized = False

    async def health_check(self) -> bool:
        if not self._initialized or not self._driver:
            return False
        try:
            await self._driver.screenshot()
            return True
        except Exception:
            return False
