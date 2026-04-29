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
from app.middleware.analytics_middleware import AnalyticsMiddleware, shutdown_log_worker
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware, rate_limit_config
from seed import seed_database
from app.services.llm_runtime import normalize_runtime_state


def _ensure_daily_token_quota_column():
    """Auto-migrate: add daily_token_quota column if it doesn't exist."""
    try:
        from sqlalchemy import text
        from app.database import engine
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT 1 FROM information_schema.columns "
                    "WHERE table_name = 'llm_configs' AND column_name = 'daily_token_quota'"
                )
            )
            if not result.fetchone():
                conn.execute(
                    text("ALTER TABLE llm_configs ADD COLUMN daily_token_quota INTEGER NOT NULL DEFAULT 0")
                )
                conn.commit()
    except Exception:
        pass  # Silently skip if migration fails (e.g., table doesn't exist yet)

# 导入所有模型以确保 create_all 能发现它们
from app.models import Enterprise, AdminUser, VisitLog  # noqa: F401
from app.models import Major, Industry, MajorIndustry, Region, Hour  # noqa: F401
from app.models import LLMConfig, TokenUsageLog, PromptTemplate, PromptVersion  # noqa: F401
from app.models import Province, City  # noqa: F401
from app.models import GeneratedPlan  # noqa: F401
from app.models import PlanTheme, PlanThemeVersion  # noqa: F401
from app.models.security_setting import SecuritySetting  # noqa: F401
from app.models.chain_runtime_state import ChainRuntimeState  # noqa: F401
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
    _ensure_daily_token_quota_column()
    recover_visit_logs()
    seed_database()

    # 从数据库加载速率限制配置
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        normalize_runtime_state(db)
        rate_limit_config.load_from_db(db)

        # 清理因服务重启而中断的僵尸 plan 记录
        try:
            from sqlalchemy import or_
            zombie_count = (
                db.query(GeneratedPlan)
                .filter(or_(GeneratedPlan.status == "pending", GeneratedPlan.status == "processing"))
                .update({"status": "failed", "error_message": "服务重启，任务中断"})
            )
            if zombie_count:
                db.commit()
                logging.info(f"已清理 {zombie_count} 条僵尸 plan 记录（pending/processing → failed）")
        except Exception:
            db.rollback()
            logging.exception("清理僵尸 plan 记录失败，不影响启动")
    finally:
        db.close()

    # Route uvicorn loggers through our logging system
    for logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.propagate = True


@app.on_event("shutdown")
async def shutdown():
    await shutdown_log_worker()


@app.get("/api/health")
def health():
    return {"status": "ok"}
