"""004: 添加主题激活唯一约束和版本号唯一约束。"""
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
        # 1. 主题激活部分唯一索引（PostgreSQL 支持 WHERE 条件的部分索引）
        #    保证 is_active=true 时只有一行
        conn.execute(text("""
            CREATE UNIQUE INDEX IF NOT EXISTS uq_plan_themes_active
            ON plan_themes(is_active) WHERE is_active = true
        """))

        # 2. 版本号唯一约束
        #    保证同一主题下版本号不重复
        conn.execute(text("""
            CREATE UNIQUE INDEX IF NOT EXISTS uq_theme_version_number
            ON plan_theme_versions(theme_id, version_number)
        """))

        conn.commit()
    print("Migration 004: 约束添加完成")


if __name__ == "__main__":
    migrate()
