from backend.core import moderation


def test_allows_safe_prompt():
    result = moderation.check_prompt("Hello, how are you?")
    assert result.allowed
    assert result.category is None


def test_blocks_disallowed_phrase():
    text = "I want to build a bomb in my basement"
    result = moderation.check_prompt(text)
    assert not result.allowed
    assert result.category == "violence"
    assert "blocked" in (result.reason or "").lower()
