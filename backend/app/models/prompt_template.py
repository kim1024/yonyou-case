"""提示词模板表。"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, func
from app.database import Base


class PromptTemplate(Base):
    """提示词模板"""
    __tablename__ = "prompt_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)                # 模板名称
    description = Column(Text)                                # 模板描述
    scene = Column(String(100))                               # 关联场景（如"课程方案生成"）
    current_version_id = Column(Integer)                      # 当前活跃版本 ID
    is_active = Column(Boolean, default=True)                 # 是否启用
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
