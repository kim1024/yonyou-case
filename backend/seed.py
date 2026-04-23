"""seed.py - 从 Excel 导入企业数据，自动创建管理员账号，初始化基础数据。"""

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
from app.models.major import Major, Industry, MajorIndustry, Region, Hour
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
        seed_majors(db)
        seed_industries(db)
        seed_regions(db)
        seed_hours(db)
    finally:
        db.close()
    _logger.info("Seed completed.")


# ---------- 基础数据 ----------

def seed_majors(db):
    """初始化专业数据（仅在表为空时执行）。"""
    if db.query(Major).first() is not None:
        _logger.info("majors table already has data, skipping.")
        return

    majors_data = [
        {"name": "大数据", "description": "聚焦数据采集、存储、分析与可视化等核心技术", "icon": "BarChart3", "sort_order": 1},
        {"name": "人工智能", "description": "聚焦机器学习、深度学习与智能应用开发", "icon": "Brain", "sort_order": 2},
        {"name": "工业互联网", "description": "聚焦工业物联网、智能制造与数字化转型", "icon": "Cpu", "sort_order": 3},
    ]
    for data in majors_data:
        db.add(Major(**data))
    db.commit()
    _logger.info("Created %d major records.", len(majors_data))


def seed_industries(db):
    """从 enterprises 表提取行业去重，创建 Industry 记录及 MajorIndustry 关联。"""
    if db.query(Industry).first() is not None:
        _logger.info("industries table already has data, skipping.")
        return

    # 从 enterprises 表中提取所有不同行业
    rows = db.query(Enterprise.industry).distinct().all()
    industry_names = sorted({r[0] for r in rows if r[0]})

    if not industry_names:
        _logger.warning("No industries found in enterprises table.")
        return

    # 获取所有专业 ID（按 sort_order 排序）
    majors = db.query(Major).order_by(Major.sort_order).all()
    major_count = len(majors)

    industry_id_map = {}
    for idx, name in enumerate(industry_names):
        industry = Industry(name=name, sort_order=idx + 1)
        db.add(industry)
        db.flush()  # 获取自增 id
        industry_id_map[name] = industry.id

    # 创建 MajorIndustry 关联：将行业轮流分配给各专业
    associations = []
    for idx, name in enumerate(industry_names):
        if major_count > 0:
            major_id = majors[idx % major_count].id
            associations.append(
                MajorIndustry(major_id=major_id, industry_id=industry_id_map[name])
            )
    if associations:
        db.add_all(associations)

    db.commit()
    _logger.info(
        "Created %d industry records and %d MajorIndustry associations.",
        len(industry_names), len(associations),
    )


def seed_regions(db):
    """从 enterprises 表提取省份去重，创建 Region 记录。"""
    if db.query(Region).first() is not None:
        _logger.info("regions table already has data, skipping.")
        return

    rows = db.query(Enterprise.province).distinct().all()
    region_names = sorted({r[0] for r in rows if r[0]})

    if not region_names:
        _logger.warning("No regions found in enterprises table.")
        return

    for idx, name in enumerate(region_names):
        db.add(Region(name=name, sort_order=idx + 1))

    db.commit()
    _logger.info("Created %d region records.", len(region_names))


def seed_hours(db):
    """初始化课时数据（仅在表为空时执行）。"""
    if db.query(Hour).first() is not None:
        _logger.info("hours table already has data, skipping.")
        return

    hours_data = [
        {"value": 8,  "label": "8课时（1天）",  "sort_order": 1},
        {"value": 16, "label": "16课时（2天）", "sort_order": 2},
        {"value": 24, "label": "24课时（3天）", "sort_order": 3},
        {"value": 32, "label": "32课时（4天）", "sort_order": 4},
    ]
    for data in hours_data:
        db.add(Hour(**data))
    db.commit()
    _logger.info("Created %d hour records.", len(hours_data))


if __name__ == "__main__":
    seed_database()
