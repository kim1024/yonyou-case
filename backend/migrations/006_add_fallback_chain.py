"""006: 添加模型降级链支持 — llm_configs 新字段 + model_fallback_settings 新表。"""
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import text
from app.database import engine


def migrate():
    with engine.connect() as conn:
        # 1. llm_configs 新增 role / fallback_order / fallback_group_id
        conn.execute(text("""
            ALTER TABLE llm_configs
            ADD COLUMN IF NOT EXISTS role VARCHAR(20) NOT NULL DEFAULT 'standalone'
        """))
        conn.execute(text("""
            ALTER TABLE llm_configs
            ADD COLUMN IF NOT EXISTS fallback_order INTEGER NOT NULL DEFAULT 0
        """))
        conn.execute(text("""
            ALTER TABLE llm_configs
            ADD COLUMN IF NOT EXISTS fallback_group_id VARCHAR(50)
        """))

        # 2. 创建 model_fallback_settings 表
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS model_fallback_settings (
                id SERIAL PRIMARY KEY,
                primary_llm_config_id INTEGER NOT NULL UNIQUE
                    REFERENCES llm_configs(id),
                failure_threshold INTEGER DEFAULT 3,
                timeout_threshold INTEGER DEFAULT 5,
                cooldown_seconds INTEGER DEFAULT 300,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """))

        conn.commit()
    print("Migration 006: 模型降级链字段和表添加完成")


if __name__ == "__main__":
    migrate()
