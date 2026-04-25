"""004: 添加主题激活唯一约束和版本号唯一约束。"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "app.db"


def migrate():
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    # 1. 主题激活部分唯一索引（SQLite 支持 WHERE 条件）
    #    保证 is_active=1 时只有一行
    cur.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_plan_themes_active
        ON plan_themes(is_active) WHERE is_active = 1
    """)

    # 2. 版本号唯一约束
    #    保证同一主题下版本号不重复
    cur.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_theme_version_number
        ON plan_theme_versions(theme_id, version_number)
    """)

    conn.commit()
    conn.close()
    print("Migration 004: 约束添加完成")


if __name__ == "__main__":
    migrate()
