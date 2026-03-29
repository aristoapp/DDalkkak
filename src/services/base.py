from __future__ import annotations

from abc import ABC, abstractmethod

from src.agent.droid_agent import DroidRunAgent
from src.agent.task_builder import TaskGoalBuilder
from src.intent.schemas import ParsedIntent
from src.memory import user_memory


class ServiceHandler(ABC):
    def __init__(self, agent: DroidRunAgent) -> None:
        self.agent = agent

    @abstractmethod
    def get_package_name(self) -> str: ...

    @abstractmethod
    def build_goal(self, intent: ParsedIntent) -> str: ...

    def get_goal(self, intent: ParsedIntent) -> str:
        """Use minitap_goal (Claude-generated) + safety suffix as primary.

        Handler.build_goal() is only a rigid template that checks entity keys;
        minitap_goal already contains the user's full intent in natural language
        (e.g. "맥도날드 검색해서 주문"), so it should take precedence.
        """
        ctx = user_memory.get_context_for_goal(intent.category)
        if intent.minitap_goal and intent.minitap_goal.strip():
            core = TaskGoalBuilder.build_goal(intent)
        else:
            core = self.build_goal(intent)
        return f"{ctx}{core}".strip()

    async def execute(self, intent: ParsedIntent) -> dict:
        goal = self.get_goal(intent)
        package_name = self.get_package_name()

        result = await self.agent.execute_task(goal=goal, package_name=package_name)

        screenshot_path = await self.agent.take_screenshot()
        result["screenshot"] = screenshot_path

        return result
