from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.middleware.rate_limit import RateLimitMiddleware


def test_rate_limit_blocks_excess_requests():
    app = FastAPI()

    @app.get("/ping")
    def ping():  # pragma: no cover - executed via test client
        return {"ok": True}

    app.add_middleware(RateLimitMiddleware, limit_per_minute=1)
    client = TestClient(app)

    assert client.get("/ping").status_code == 200
    blocked = client.get("/ping")
    assert blocked.status_code == 429
    assert blocked.json()["error"]["code"] == "rate_limited"
