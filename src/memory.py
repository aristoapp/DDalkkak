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

    def _extract(self, key: str) -> str:
        """Extract the value of `- **key**: value` from the raw markdown."""
        for line in self._raw.splitlines():
            m = re.match(rf"^-\s+\*\*{re.escape(key)}\*\*:\s*(.+)", line.strip())
            if m:
                return m.group(1).strip()
        return ""

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
        """Compact, category-relevant context for Droid agent goals.

        Only includes fields the Droid agent actually needs for the given
        category so the goal string stays short and focused.
        """
        if not self._raw:
            return ""

        name = self._extract("이름")
        phone = self._extract("전화번호")
        home = self._extract("거주지(집)")
        work = self._extract("직장(회사)")
        likes = self._extract("좋아하는 음식")
        dislikes = self._extract("싫어하거나 못 먹는 음식")
        gf_pref = self._extract("여자친구 식사 취향")

        blocks: dict[ServiceCategory, str] = {
            ServiceCategory.DELIVERY: (
                f"배달주소(기본): {home}. "
                f"선호 음식: {likes}. 기피 음식: {dislikes}. "
                f"여자친구 동반 시: {gf_pref}."
            ),
            ServiceCategory.MOBILITY: (
                f"집: {home}. 회사: {work}. "
                f"이름: {name}. 전화: {phone}."
            ),
            ServiceCategory.RESERVATION: (
                f"선호: {likes}. 기피: {dislikes}. "
                f"여자친구 동반 시: {gf_pref}."
            ),
            ServiceCategory.SHOPPING: (
                f"배송지: {home}. "
                f"이름: {name}. 전화: {phone}."
            ),
            ServiceCategory.TRAVEL: f"예약자: {name}. 연락처: {phone}.",
            ServiceCategory.GIFT: f"보내는 사람: {name}. 연락처: {phone}.",
        }
        ctx = blocks.get(category)
        if not ctx:
            return ""
        return f"[사용자 정보] {ctx}\n"


user_memory = UserMemory()
