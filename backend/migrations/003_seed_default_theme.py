"""迁移脚本：初始化方案样式默认主题数据。

功能：
  1. 在 plan_themes 表中插入一条默认主题 "经典红色"
  2. 在 plan_theme_versions 表中插入对应的版本记录（包含 style_config JSON）
  3. 将版本 ID 回写到主题的 current_version_id 字段

幂等性：若 plan_themes 表已有数据则跳过。

用法：
    cd backend && python migrations/003_seed_default_theme.py
"""

import json
import logging
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
_logger = logging.getLogger(__name__)

# ---------- 默认主题配置 ----------

DEFAULT_THEME_NAME = "经典红色"
DEFAULT_THEME_DESCRIPTION = "系统默认主题，红色主色调"

DEFAULT_STYLE_CONFIG = {
    "accentColor": "#C0392B",
    "highlightColor": "#C0392B",
    "dotColor": "#D4A06A",
    "pricingCardBg": "linear-gradient(135deg, #B83227 0%, #C0392B 35%, #D94A3F 100%)",
    "pricingNumberGradient": "linear-gradient(180deg, #FFE066 0%, #FFD700 40%, #DAA520 100%)",
    "pageBg": "#F8F7F4",
    "cardBg": "#FFFFFF",
    "textColor": "#444444",
    "subtitleColor": "#2D2D2D",
}


def migrate():
    """执行迁移：插入默认方案样式主题及版本。"""
    from app.database import SessionLocal
    from app.models.plan_theme import PlanTheme
    from app.models.plan_theme_version import PlanThemeVersion

    db = SessionLocal()
    try:
        # 幂等性检查
        if db.query(PlanTheme).first() is not None:
            _logger.info("plan_themes 表已有数据，跳过默认主题初始化。")
            return

        # 1. 创建主题记录
        theme = PlanTheme(
            name=DEFAULT_THEME_NAME,
            description=DEFAULT_THEME_DESCRIPTION,
            is_active=True,
        )
        db.add(theme)
        db.flush()  # 获取 theme.id

        # 2. 创建版本记录
        version = PlanThemeVersion(
            theme_id=theme.id,
            version_number=1,
            style_config=json.dumps(DEFAULT_STYLE_CONFIG, ensure_ascii=False),
            remark="默认版本（系统初始化）",
            created_by="system",
        )
        db.add(version)
        db.flush()  # 获取 version.id

        # 3. 将版本 ID 回写到主题
        theme.current_version_id = version.id

        db.commit()
        _logger.info(
            "已创建默认主题 '%s'（id=%d）及版本 1（version_id=%d）。",
            DEFAULT_THEME_NAME, theme.id, version.id,
        )
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    _logger.info("=== 开始迁移：初始化方案样式默认主题 ===")
    migrate()
    _logger.info("=== 迁移脚本执行完毕 ===")
