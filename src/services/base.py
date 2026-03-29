from __future__ import annotations

from abc import ABC, abstractmethod

from src.agent.appium_agent import AppiumAgent
from src.agent.task_builder import TaskGoalBuilder
from src.intent.schemas import ParsedIntent


class ServiceHandler(ABC):
    def __init__(self, agent: AppiumAgent) -> None:
        self.agent = agent

    @abstractmethod
    def get_bundle_id(self) -> str: ...

    @abstractmethod
    def build_goal(self, intent: ParsedIntent) -> str: ...

    def get_goal(self, intent: ParsedIntent) -> str:
        """Handler.build_goal() is primary; TaskGoalBuilder is fallback for unhandled services."""
        return self.build_goal(intent)

    @staticmethod
    def get_fallback_goal(intent: ParsedIntent) -> str:
        return TaskGoalBuilder.build_goal(intent)

    async def execute(self, intent: ParsedIntent) -> dict:
        goal = self.get_goal(intent)
        bundle_id = self.get_bundle_id()

        result = await self.agent.execute_task(goal=goal, bundle_id=bundle_id)

        screenshot_path = await self.agent.take_screenshot()
        result["screenshot"] = screenshot_path

        return result
