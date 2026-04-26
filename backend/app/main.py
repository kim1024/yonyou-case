import logging
import sys
from pathlib import Path

# 将 backend/ 加入 sys.path，确保 seed 模块可被导入
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.logging_config import setup_logging

# Initialize logging before any other imports so logs are captured during startup
setup_logging()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base, recover_visit_logs
from app.routers import admin_auth, wizard, admin_analytics, admin_enterprises
from app.routers import admin_majors, admin_industries, admin_regions, admin_hours
from app.routers import admin_prompts, admin_llm, admin_provinces
from app.routers import admin_llm_chains
from app.routers import admin_plans
from app.routers import admin_themes
from app.middleware.analytics_middleware import AnalyticsMiddleware
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware, rate_limit_config
from seed import seed_database

# 导入所有模型以确保 create_all 能发现它们
from app.models import Enterprise, AdminUser, VisitLog  # noqa: F401
from app.models import Major, Industry, MajorIndustry, Region, Hour  # noqa: F401
from app.models import LLMConfig, TokenUsageLog, PromptTemplate, PromptVersion  # noqa: F401
from app.models import Province, City  # noqa: F401
from app.models import GeneratedPlan  # noqa: F401
from app.models import PlanTheme, PlanThemeVersion  # noqa: F401
from app.models.security_setting import SecuritySetting  # noqa: F401
from app.routers import admin_security

app = FastAPI(title="用友案例定制系统 API")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=settings.get("server", {}).get("cors_origins", ["http://localhost:5173"]),
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Register request logging middleware (after CORS, before Analytics)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

# 注册路由
app.include_router(admin_auth.router)
app.include_router(wizard.router)
app.include_router(admin_analytics.router)
app.include_router(admin_enterprises.router)
app.include_router(admin_majors.router)
app.include_router(admin_industries.router)
app.include_router(admin_regions.router)
app.include_router(admin_hours.router)
app.include_router(admin_prompts.router)
app.include_router(admin_prompts.public_router)
app.include_router(admin_llm.router)
app.include_router(admin_llm_chains.router)
app.include_router(admin_provinces.router)
app.include_router(admin_plans.router)
app.include_router(admin_themes.router)
app.include_router(admin_themes.public_router)
app.include_router(admin_security.router)

# 注册分析中间件
app.add_middleware(AnalyticsMiddleware)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    recover_visit_logs()
    seed_database()

    # 从数据库加载速率限制配置
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        rate_limit_config.load_from_db(db)
    finally:
        db.close()

    # Route uvicorn loggers through our logging system
    for logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.propagate = True


@app.get("/api/health")
def health():
    return {"status": "ok"}
