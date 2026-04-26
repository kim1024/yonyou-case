"""005: 添加 client_request_id 字段到 generated_plans 表。"""
import sys
from pathlib import Path

# 确保 backend/ 在 sys.path 中
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import text
from app.database import engine


def migrate():
    with engine.connect() as conn:
        # 1. 添加 client_request_id 列
        conn.execute(text("""
            ALTER TABLE generated_plans
            ADD COLUMN IF NOT EXISTS client_request_id VARCHAR(36)
        """))

        # 2. 创建索引
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_generated_plans_client_request_id
            ON generated_plans(client_request_id)
        """))

        conn.commit()
    print("Migration 005: client_request_id 字段添加完成")


if __name__ == "__main__":
    migrate()
