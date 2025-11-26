from __future__ import annotations

import re
from dataclasses import dataclass

from backend.config.settings import get_settings

settings = get_settings()


@dataclass
class ModerationResult:
    allowed: bool
    category: str | None = None
    reason: str | None = None


class ModerationError(Exception):
    def __init__(self, message: str, *, category: str | None = None) -> None:
        super().__init__(message)
        self.category = category


# Extremely small heuristic list to prevent obviously disallowed prompts without external APIs.
_PATTERN_RULES: list[tuple[str, re.Pattern[str], str]] = [
    (
        "self_harm",
        re.compile(r"(kill myself|suicide|self-harm|end my life)", re.IGNORECASE),
        "We can't help with requests related to self-harm.",
    ),
    (
        "violence",
        re.compile(r"(build(?:ing)?\s+a\s+bomb|make\s+an\s+explosive|assassinate)", re.IGNORECASE),
        "Violent or weapon-building instructions are blocked.",
    ),
    (
        "hate",
        re.compile(r"(hate\s+speech|kill all|genocide)", re.IGNORECASE),
        "Hateful or harassing content is not permitted.",
    ),
    (
        "sexual_minors",
        re.compile(r"(minor\s+sexual|child\s+sexual)", re.IGNORECASE),
        "Sexual content involving minors is strictly disallowed.",
    ),
]


def check_prompt(text: str) -> ModerationResult:
    if not text:
        return ModerationResult(allowed=True)

    normalized = text.strip()
    for category, pattern, reason in _PATTERN_RULES:
        if pattern.search(normalized):
            return ModerationResult(allowed=False, category=category, reason=reason)

    if len(normalized) > 8000:
        return ModerationResult(
            allowed=False,
            category="length",
            reason="Prompt exceeds maximum supported length.",
        )

    return ModerationResult(allowed=True)


def enforce_safe_prompt(text: str) -> None:
    if not settings.moderation_enabled:
        return
    result = check_prompt(text)
    if not result.allowed:
        raise ModerationError(result.reason or "Prompt rejected", category=result.category)
