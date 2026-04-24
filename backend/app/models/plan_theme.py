"""方案样式主题表。"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, func
from app.database import Base


class PlanTheme(Base):
    """方案样式主题"""
    __tablename__ = "plan_themes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)                     # 主题名称
    description = Column(Text)                                     # 主题描述
    is_active = Column(Boolean, default=False)                     # 是否激活（同一时间仅一个为 True）
    current_version_id = Column(Integer)                           # 当前使用的版本 ID
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
