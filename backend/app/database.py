from pathlib import Path
import json
import logging
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

_logger = logging.getLogger(__name__)

# 数据库文件目录：项目根目录下的 backend/data/
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

db_url = settings.get("database", {}).get("url", "")

engine = create_engine(
    db_url,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI 依赖注入：获取数据库会话。"""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


JSONL_PATH = DATA_DIR / "visit_logs.jsonl"


def recover_visit_logs():
    """从 JSONL 备份文件恢复 visit_logs 表数据（仅在表为空时执行）。"""
    try:
        from app.models.analytics import VisitLog

        db = SessionLocal()
        try:
            if db.query(VisitLog).first() is not None:
                return  # 表已有数据，无需恢复

            if not JSONL_PATH.exists():
                return

            lines = [line.strip() for line in JSONL_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
            if not lines:
                return

            logs = []
            for line in lines:
                try:
                    data = json.loads(line)
                    timestamp_str = data.get("timestamp", "")
                    request_ts = None
                    if timestamp_str:
                        try:
                            request_ts = datetime.fromisoformat(timestamp_str)
                        except (ValueError, TypeError):
                            pass

                    log = VisitLog(
                        endpoint=data.get("endpoint", ""),
                        method=data.get("method", ""),
                        ip_address=data.get("ip_address", ""),
                        user_agent=data.get("user_agent", ""),
                        industry=data.get("industry", ""),
                        region=data.get("region", ""),
                        enterprise=data.get("enterprise", ""),
                        major=data.get("major", ""),
                        hour=data.get("hour", ""),
                        request_timestamp=request_ts,
                    )
                    logs.append(log)
                except (json.JSONDecodeError, KeyError):
                    continue

            if logs:
                db.add_all(logs)
                db.commit()
                _logger.info("Recovered %d visit_logs records from JSONL backup.", len(logs))
        finally:
            db.close()
    except Exception:
        _logger.exception("Failed to recover visit_logs from JSONL backup")
