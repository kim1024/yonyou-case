"""方案样式主题版本表。"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index, func
from app.database import Base


class PlanThemeVersion(Base):
    """方案样式主题版本"""
    __tablename__ = "plan_theme_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    theme_id = Column(Integer, ForeignKey("plan_themes.id"), nullable=False)    # 关联主题
    version_number = Column(Integer, nullable=False)                            # 版本号（自增）
    style_config = Column(Text, nullable=False)                                 # 样式配置 JSON
    remark = Column(Text)                                                       # 版本备注
    created_by = Column(String(100))                                            # 创建人
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("idx_plan_theme_versions_theme_id", "theme_id"),
    )
