"""专业、行业、地区、课时 数据模型。"""

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint, func
)
from app.database import Base


class Major(Base):
    """专业表"""
    __tablename__ = "majors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)  # 专业名称
    description = Column(Text)  # 专业描述
    icon = Column(String(50))  # 图标名称（lucide图标名）
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Industry(Base):
    """行业表"""
    __tablename__ = "industries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)  # 行业名称
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class MajorIndustry(Base):
    """专业-行业多对多关联表"""
    __tablename__ = "major_industries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    major_id = Column(Integer, ForeignKey("majors.id"), nullable=False)
    industry_id = Column(Integer, ForeignKey("industries.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("major_id", "industry_id", name="uq_major_industry"),
    )


class Region(Base):
    """地区（省份）表"""
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)  # 省份名称
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Hour(Base):
    """课时表"""
    __tablename__ = "hours"

    id = Column(Integer, primary_key=True, autoincrement=True)
    value = Column(Integer, unique=True, nullable=False)  # 课时数
    label = Column(String(50))  # 显示标签
    unit_price = Column(Integer, default=2000)  # 课时单价（元）
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
