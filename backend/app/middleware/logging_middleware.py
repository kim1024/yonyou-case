import logging
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


SKIP_PATHS = frozenset({"/health", "/api/health", "/docs", "/openapi.json", "/redoc"})


class LoggingMiddleware(BaseHTTPMiddleware):
    """Logs request details: method, path, status code, duration, client IP, user agent."""

    def __init__(self, app):
        super().__init__(app)
        self.logger = logging.getLogger("app.access")

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Skip health check and docs paths
        if path in SKIP_PATHS or path.startswith("/docs") or path.startswith("/redoc"):
            return await call_next(request)

        # Capture request metadata BEFORE call_next (request object may not be safe after)
        method = request.method
        query_string = request.url.query if request.url.query else ""
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "")

        start_time = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        status_code = response.status_code
        log_msg = (
            f"{method} {path} | {query_string} | "
            f"status={status_code} | {duration_ms}ms | "
            f"ip={client_ip} | ua={user_agent}"
        )

        if status_code >= 500:
            self.logger.error(log_msg)
        elif status_code >= 400:
            self.logger.warning(log_msg)
        else:
            self.logger.info(log_msg)

        return response
