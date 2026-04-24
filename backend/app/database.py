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

    # --- llm_configs 表 ---
    cursor.execute("PRAGMA table_info(llm_configs)")
    columns = {row[1] for row in cursor.fetchall()}
    if not columns:
        cursor.execute("""
            CREATE TABLE llm_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                api_base_url TEXT NOT NULL,
                api_key TEXT NOT NULL,
                model VARCHAR(100) NOT NULL,
                temperature FLOAT DEFAULT 0.7,
                max_tokens INTEGER DEFAULT 2000,
                timeout INTEGER DEFAULT 60,
                is_active BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

    # --- token_usage_logs 表 ---
    cursor.execute("PRAGMA table_info(token_usage_logs)")
    columns = {row[1] for row in cursor.fetchall()}
    if not columns:
        cursor.execute("""
            CREATE TABLE token_usage_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                llm_config_id INTEGER NOT NULL REFERENCES llm_configs(id),
                model VARCHAR(100) NOT NULL,
                prompt_tokens INTEGER DEFAULT 0,
                completion_tokens INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0,
                request_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON token_usage_logs(request_timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_model ON token_usage_logs(model)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_llm_config_id ON token_usage_logs(llm_config_id)")
        conn.commit()

    # --- prompt_templates 表 ---
    cursor.execute("PRAGMA table_info(prompt_templates)")
    columns = {row[1] for row in cursor.fetchall()}
    if not columns:
        cursor.execute("""
            CREATE TABLE prompt_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                scene VARCHAR(100),
                current_version_id INTEGER,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

    # --- prompt_versions 表 ---
    cursor.execute("PRAGMA table_info(prompt_versions)")
    columns = {row[1] for row in cursor.fetchall()}
    if not columns:
        cursor.execute("""
            CREATE TABLE prompt_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER NOT NULL REFERENCES prompt_templates(id),
                version_number INTEGER NOT NULL,
                content TEXT NOT NULL,
                variables TEXT,
                remark TEXT,
                created_by VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_template_id ON prompt_versions(template_id)")
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_template_version ON prompt_versions(template_id, version_number)")
        conn.commit()

    # --- provinces 表 ---
    cursor.execute("PRAGMA table_info(provinces)")
    columns = {row[1] for row in cursor.fetchall()}
    if not columns:
        cursor.execute("""
            CREATE TABLE provinces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL UNIQUE,
                sort_order INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

    # --- cities 表 ---
    cursor.execute("PRAGMA table_info(cities)")
    columns = {row[1] for row in cursor.fetchall()}
    if not columns:
        cursor.execute("""
            CREATE TABLE cities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                province_id INTEGER NOT NULL REFERENCES provinces(id),
                sort_order INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_province_id ON cities(province_id)")
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_province_city ON cities(province_id, name)")
        conn.commit()

    conn.close()


def get_db():
    """FastAPI 依赖注入：获取数据库会话。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
