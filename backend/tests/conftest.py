import importlib
import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Keep heavy pipelines disabled during tests to avoid OOM and long downloads.
os.environ.setdefault("IMAGE_ENABLED", "false")
os.environ.setdefault("CHAT_DEVICE", "cpu")
os.environ.setdefault("CHAT_PRECISION", "float32")
os.environ.setdefault("DB_URL", "sqlite:///./test.db")


@pytest.fixture(scope="session")
def test_app():
    """Provide a FastAPI app instance with fresh settings for each test run."""
    from backend.config import settings as settings_module

    settings_module.get_settings.cache_clear()
    from backend.db import session as db_session

    importlib.reload(db_session)
    db_session.reset_database()
    from backend import main

    importlib.reload(main)
    return main.app


@pytest.fixture()
def client(test_app, monkeypatch):
    """FastAPI test client with core ML primitives mocked for speed."""
    from backend.api import chat, translate

    monkeypatch.setattr(chat, "detect_language", lambda *_: "en")
    monkeypatch.setattr(chat, "translate_text", lambda text, *_: text)
    monkeypatch.setattr(chat, "generate_reply", lambda *args, **kwargs: "stub reply")

    def _fake_stream(*_args, **_kwargs):
        yield "stub reply"

    monkeypatch.setattr(chat, "stream_reply", _fake_stream)
    monkeypatch.setattr(translate, "translate_text", lambda text, _from, to: f"{text}-{to}")

    client = TestClient(test_app)

    signup_payload = {"email": "tester@example.com", "password": "secret123", "full_name": "Tester"}
    resp = client.post("/auth/signup", json=signup_payload)
    if resp.status_code == 400:  # user already exists in this test scope
        resp = client.post("/auth/login", json=signup_payload)
    tokens = resp.json()
    client.headers.update({"Authorization": f"Bearer {tokens['access_token']}"})
    return client
