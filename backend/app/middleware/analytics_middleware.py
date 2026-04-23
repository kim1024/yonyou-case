from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import json
from app.database import SessionLocal
from app.models.analytics import VisitLog


class AnalyticsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 只记录 /api/ 且不记录 /api/admin/
        path = request.url.path
        if not path.startswith("/api/") or path.startswith("/api/admin/"):
            return await call_next(request)

        # 先读取 body（在 call_next 之前）
        body_bytes = b""
        if request.method == "POST":
            try:
                body_bytes = await request.body()
            except Exception:
                pass

        response = await call_next(request)

        # 异步记录，不阻塞响应
        try:
            log_data = {
                "endpoint": path,
                "method": request.method,
                "ip_address": request.client.host if request.client else "",
                "user_agent": request.headers.get("user-agent", ""),
            }

            # 解析缓存的 body
            if request.method == "POST" and body_bytes:
                try:
                    data = json.loads(body_bytes)
                    log_data["industry"] = data.get("industry", "")
                    log_data["region"] = data.get("province", "")
                    log_data["enterprise"] = data.get("name", data.get("enterprise", ""))
                    log_data["major"] = data.get("major", "")
                    log_data["hour"] = str(data.get("hour", ""))
                except Exception:
                    pass

            import asyncio
            def write_log():
                db = SessionLocal()
                try:
                    log = VisitLog(**log_data)
                    db.add(log)
                    db.commit()
                except Exception:
                    db.rollback()
                finally:
                    db.close()
            asyncio.create_task(asyncio.to_thread(write_log))
        except Exception:
            pass

        return response
