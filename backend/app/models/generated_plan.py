from sqlalchemy import Column, Integer, String, Text, DateTime, Index, func
from app.database import Base


class GeneratedPlan(Base):
    __tablename__ = 'generated_plans'

    id = Column(Integer, primary_key=True, autoincrement=True)
    major = Column(String(100))
    industry = Column(String(100))
    enterprise = Column(String(200))
    province = Column(String(50))
    hour = Column(Integer)
    source = Column(String(20))  # "ai" 或 "template"
    plan_title = Column(String(500))
    plan_data = Column(Text)  # 完整方案 JSON 字符串
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index('idx_generated_plans_source', 'source'),
        Index('idx_generated_plans_created_at', 'created_at'),
        Index('idx_generated_plans_industry', 'industry'),
        Index('idx_generated_plans_province', 'province'),
    )
