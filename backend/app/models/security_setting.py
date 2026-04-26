"""安全设置配置表（key-value）。"""
from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base


class SecuritySetting(Base):
    __tablename__ = "security_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(String(500), nullable=False)
    description = Column(String(200), default="")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
