from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.middleware.security_headers import SecurityHeadersMiddleware


def test_security_headers_applied_to_responses():
    app = FastAPI()

    @app.get("/ping")
    def ping():  # pragma: no cover - executed via client
        return {"ok": True}

    app.add_middleware(SecurityHeadersMiddleware)
    client = TestClient(app)

    response = client.get("/ping")

    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["Strict-Transport-Security"].startswith("max-age=")
    assert "default-src 'self'" in response.headers["Content-Security-Policy"]
    assert response.headers["Permissions-Policy"] == "camera=(), microphone=(), geolocation=()"
```