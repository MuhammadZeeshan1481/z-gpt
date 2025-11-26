from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Attach opinionated security headers to every response."""

    def __init__(
        self,
        app,
        *,
        csp: str | None = None,
        hsts_max_age: int = 63072000,
        include_subdomains: bool = True,
        preload: bool = True,
    ) -> None:
        super().__init__(app)
        self.csp = csp or (
            "default-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'none'; "
            "form-action 'self'; "
            "connect-src 'self'; "
            "img-src 'self' data:; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'"
        )
        hsts_parts = [f"max-age={hsts_max_age}"]
        if include_subdomains:
            hsts_parts.append("includeSubDomains")
        if preload:
            hsts_parts.append("preload")
        self.hsts_value = "; ".join(hsts_parts)
        self.static_headers: dict[str, str] = {
            "Content-Security-Policy": self.csp,
            "Strict-Transport-Security": self.hsts_value,
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Referrer-Policy": "no-referrer",
            "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
            "Cross-Origin-Resource-Policy": "same-origin",
            "Cross-Origin-Opener-Policy": "same-origin",
            "Cross-Origin-Embedder-Policy": "require-corp",
        }

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        for header, value in self.static_headers.items():
            response.headers.setdefault(header, value)
        return response
