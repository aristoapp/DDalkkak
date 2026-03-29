from __future__ import annotations

import re
from pathlib import Path

from src.intent.schemas import ServiceCategory


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


class UserMemory:
    """Loads `memory.md` from the project root for agent personalization."""

    def __init__(self, memory_path: Path | None = None) -> None:
        self._path = memory_path or (_project_root() / "memory.md")
        self._raw: str = ""
        self.reload()

    def reload(self) -> None:
        if self._path.is_file():
            self._raw = self._path.read_text(encoding="utf-8").strip()
        else:
            self._raw = ""

    def _bullet_lines(self) -> list[str]:
        """Extract `- **key**: value` style lines from markdown for compact agent context."""
        out: list[str] = []
        for line in self._raw.splitlines():
            s = line.strip()
            if re.match(r"^-\s+\*\*[^*]+\*\*:", s):
                out.append(s)
        return out

    def _bullet_summary(self, max_chars: int = 900) -> str:
        parts = self._bullet_lines()
        if not parts:
            return ""
        text = " ".join(parts)
        if len(text) <= max_chars:
            return text
        return text[: max_chars - 3].rstrip() + "..."

    def get_profile_prompt(self) -> str:
        """Append to intent parser system prompt so Claude knows the user."""
        if not self._raw:
            return ""
        return (
            "\n\n[사용자 프로필 — 아래 내용을 인텐트 해석·추천·엔티티 추출에 반영하세요]\n"
            f"{self._raw}\n"
            "[끝 사용자 프로필]\n"
        )

    def get_context_for_goal(self, category: ServiceCategory) -> str:
        """Category-specific lead-in + bullet summary from `memory.md` for Droid goals."""
        summary = self._bullet_summary()
        if not summary:
            return ""

        leads: dict[ServiceCategory, str] = {
            ServiceCategory.DELIVERY: (
                "배달 주소·음식 선호·기피 음식·동반 식사 맥락을 아래 프로필에 맞게 반영하세요. "
            ),
            ServiceCategory.MOBILITY: (
                "출발지/목적지가 없으면 집·회사 주소를 활용하세요. 연락처는 예약/호출에 사용 가능합니다. "
            ),
            ServiceCategory.RESERVATION: (
                "식당 유형·기피 음식·동반자(여자친구) 취향을 반영하세요. "
            ),
            ServiceCategory.SHOPPING: (
                "배송지·수령인 정보가 필요하면 아래 프로필을 사용하세요. "
            ),
            ServiceCategory.TRAVEL: (
                "예약자 정보가 필요하면 아래 프로필을 사용하세요. "
            ),
            ServiceCategory.GIFT: (
                "보내는 사람·연락처가 필요하면 아래 프로필을 사용하세요. "
            ),
        }
        lead = leads.get(category, "아래 사용자 프로필을 참고하세요. ")
        return f"[사용자 맥락] {lead}{summary}\n\n"


user_memory = UserMemory()
