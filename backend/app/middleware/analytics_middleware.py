from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import json
from app.database import SessionLocal
from app.models.analytics import VisitLog


class AnalyticsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # 只记录 /api/ 且不记录 /api/admin/
        path = request.url.path
        if not path.startswith("/api/") or path.startswith("/api/admin/"):
            return response

        # 异步记录，不阻塞响应
        try:
            log_data = {
                "endpoint": path,
                "method": request.method,
                "ip_address": request.client.host if request.client else "",
                "user_agent": request.headers.get("user-agent", ""),
            }

            # 对 POST 请求尝试解析请求体
            if request.method == "POST":
                try:
                    body = await request.body()
                    if body:
                        data = json.loads(body)
                        log_data["industry"] = data.get("industry", "")
                        log_data["region"] = data.get("province", "")  # 字段名映射
                        log_data["enterprise"] = data.get("name", data.get("enterprise", ""))
                        log_data["major"] = data.get("major", "")
                        log_data["hour"] = str(data.get("hour", ""))
                except Exception:
                    pass

            db = SessionLocal()
            try:
                log = VisitLog(**log_data)
                db.add(log)
                db.commit()
            finally:
                db.close()
        except Exception:
            pass

        return response
