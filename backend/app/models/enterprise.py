from sqlalchemy import Column, Integer, String, Text, DateTime, func, Index
from app.database import Base


class Enterprise(Base):
    __tablename__ = "enterprises"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_name = Column(String, nullable=False)       # 客户名称
    province = Column(String, nullable=False)             # 客户所在省
    city = Column(String, nullable=False)                 # 客户所在市
    industry = Column(String, nullable=False)             # 标准行业
    company_intro = Column(Text)                          # 企业简介
    yonyou_content = Column(Text)                         # 用友建设内容
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_enterprises_industry", "industry"),
        Index("idx_enterprises_province", "province"),
        Index("idx_enterprises_industry_province_name", "industry", "province", "customer_name"),
    )
