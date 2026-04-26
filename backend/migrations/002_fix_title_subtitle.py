"""迁移脚本：修正 prompt_versions 中 title/subtitle 的格式。

问题：数据库模板中 title 和 subtitle 格式错误：
  旧: title = "{enterprise_name}案例教学课程方案", subtitle = "{enterprise_name}"
  新: title = "{enterprise_name}案例", subtitle = "教学课程方案"

用法：
    cd backend && python migrations/002_fix_title_subtitle.py
"""

import logging
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import create_engine, text

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
_logger = logging.getLogger(__name__)

OLD_TITLE = '"title": "{enterprise_name}案例教学课程方案"'
NEW_TITLE = '"title": "{enterprise_name}案例"'

OLD_SUBTITLE = '"subtitle": "{enterprise_name}"'
NEW_SUBTITLE = '"subtitle": "教学课程方案"'


def main():
    from app.config import settings
    db_url = settings.get("database", {}).get("url", "")
    if not db_url:
        _logger.error("未配置数据库连接 URL，请检查 config.yaml")
        sys.exit(1)
    _logger.info("数据库: %s", db_url.split("@")[-1] if "@" in db_url else db_url)

    engine = create_engine(db_url)
    with engine.begin() as conn:
        rows = conn.execute(
            text("SELECT id, content FROM prompt_versions WHERE content LIKE :pat"),
            {"pat": "%案例教学课程方案%"},
        ).fetchall()

        if not rows:
            _logger.info("没有需要修正的记录，跳过")
            return

        _logger.info("发现 %d 条需要修正的记录", len(rows))
        for row in rows:
            new_content = row.content.replace(OLD_TITLE, NEW_TITLE).replace(OLD_SUBTITLE, NEW_SUBTITLE)
            conn.execute(
                text("UPDATE prompt_versions SET content = :c WHERE id = :id"),
                {"c": new_content, "id": row.id},
            )
            _logger.info("  已修正 prompt_versions.id = %d", row.id)

    _logger.info("迁移完成")


if __name__ == "__main__":
    main()
