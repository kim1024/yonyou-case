"""提示词版本表。"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index, UniqueConstraint, func
from app.database import Base


class PromptVersion(Base):
    """提示词版本"""
    __tablename__ = "prompt_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    template_id = Column(Integer, ForeignKey("prompt_templates.id"), nullable=False)  # 关联模板
    version_number = Column(Integer, nullable=False)           # 版本号（自增）
    content = Column(Text, nullable=False)                     # 提示词完整内容
    variables = Column(Text)                                   # 变量占位符说明（JSON 字符串）
    remark = Column(Text)                                      # 版本备注
    created_by = Column(String(100))                           # 创建人
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("idx_template_id", "template_id"),
        UniqueConstraint("template_id", "version_number", name="uq_template_version"),
    )
