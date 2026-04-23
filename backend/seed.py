"""seed.py - 从 Excel 导入企业数据，并自动创建管理员账号。"""

import logging
import sys
from pathlib import Path

# 将 backend/ 加入 sys.path，确保 `app.*` 可被导入
BACKEND_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_DIR))

from app.logging_config import setup_logging

setup_logging()

_logger = logging.getLogger(__name__)

import yaml
from openpyxl import load_workbook

from app.database import Base, engine, SessionLocal
from app.models.enterprise import Enterprise
from app.models.admin import AdminUser
from app.services.auth_service import get_password_hash

# ---------- 路径 ----------
PROJECT_ROOT = BACKEND_DIR.parent
EXCEL_PATH = PROJECT_ROOT / "old" / "data" / "data.xlsx"
CONFIG_PATH = PROJECT_ROOT / "config.yaml"

# Excel 中文列名 → 模型字段映射
COLUMN_MAP = {
    "客户名称": "customer_name",
    "客户所在省": "province",
    "客户所在市": "city",
    "标准行业": "industry",
    "企业简介": "company_intro",
    "用友建设内容": "yonyou_content",
}


def _load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def seed_enterprises(db):
    """从 Excel 导入企业数据（仅在表为空时执行）。"""
    if db.query(Enterprise).first() is not None:
        _logger.info("enterprises table already has data, skipping import.")
        return

    if not EXCEL_PATH.exists():
        _logger.error("Excel file not found: %s", EXCEL_PATH)
        return

    wb = load_workbook(EXCEL_PATH, read_only=True)
    ws = wb.active

    # 读取表头
    headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    header_index = {h: i for i, h in enumerate(headers) if h}

    enterprises = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        kwargs = {}
        for cn_name, field in COLUMN_MAP.items():
            idx = header_index.get(cn_name)
            if idx is not None:
                kwargs[field] = row[idx] if row[idx] is not None else ""
        # 至少需要 customer_name
        if kwargs.get("customer_name"):
            enterprises.append(Enterprise(**kwargs))

    wb.close()

    if enterprises:
        db.add_all(enterprises)
        db.commit()
        _logger.info("Successfully imported %d enterprise records.", len(enterprises))
    else:
        _logger.warning("No valid data parsed from Excel.")


def seed_admin(db):
    """如果 admin_users 表为空，则从 config.yaml 创建管理员账号。"""
    if db.query(AdminUser).first() is not None:
        _logger.info("admin_users table already has data, skipping creation.")
        return

    config = _load_config()
    admin_cfg = config.get("admin", {})
    username = admin_cfg.get("username", "admin")
    password = admin_cfg.get("password", "changeme")

    user = AdminUser(
        username=username,
        password_hash=get_password_hash(password),
    )
    db.add(user)
    db.commit()
    _logger.info("Created admin user: %s", username)


def seed_database():
    """主入口：建表 + 导入数据。"""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_enterprises(db)
        seed_admin(db)
    finally:
        db.close()
    _logger.info("Seed completed.")


if __name__ == "__main__":
    seed_database()
