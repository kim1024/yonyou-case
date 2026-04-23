from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.routers import admin_auth, wizard, admin_analytics, admin_enterprises
from app.middleware.analytics_middleware import AnalyticsMiddleware

# 导入所有模型以确保 create_all 能发现它们
from app.models import Enterprise, AdminUser, VisitLog  # noqa: F401

app = FastAPI(title="用友案例定制系统 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get("server", {}).get("cors_origins", ["http://localhost:5173"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(admin_auth.router)
app.include_router(wizard.router)
app.include_router(admin_analytics.router)
app.include_router(admin_enterprises.router)

# 注册分析中间件
app.add_middleware(AnalyticsMiddleware)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/api/health")
def health():
    return {"status": "ok"}
