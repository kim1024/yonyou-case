from pathlib import Path
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 数据库文件目录：项目根目录下的 backend/data/
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "app.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite 特有
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def migrate_db():
    """自动迁移：为已有表添加新列（SQLite 不支持 ALTER ADD COLUMN IF NOT EXISTS，需逐列检查）。"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # 检查 hours 表是否有 unit_price 列
    cursor.execute("PRAGMA table_info(hours)")
    columns = {row[1] for row in cursor.fetchall()}
    if "unit_price" not in columns:
        cursor.execute("ALTER TABLE hours ADD COLUMN unit_price INTEGER DEFAULT 2000")
        conn.commit()

    conn.close()


def get_db():
    """FastAPI 依赖注入：获取数据库会话。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
