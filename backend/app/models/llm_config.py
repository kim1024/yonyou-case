"""大模型配置表。"""

from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, func
from app.database import Base


class LLMConfig(Base):
    """大模型配置"""
    __tablename__ = "llm_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)               # 配置名称（如"主力模型"、"备用模型"）
    api_base_url = Column(Text, nullable=False)               # API 基础地址
    api_key = Column(Text, nullable=False)                    # API 密钥（明文存储，前端掩码显示）
    model = Column(String(100), nullable=False)               # 模型名称
    temperature = Column(Float, default=0.7)                  # 温度参数
    max_tokens = Column(Integer, default=2000)                # 最大 token 数
    timeout = Column(Integer, default=60)                     # 超时秒数
    is_active = Column(Boolean, default=False)                # 是否为当前使用的配置
    role = Column(String(20), default="standalone", nullable=False)  # "primary" | "fallback" | "standalone"
    fallback_order = Column(Integer, default=0, nullable=False)      # 0=primary/standalone, 1..N for fallbacks
    fallback_group_id = Column(String(50), nullable=True)            # UUID-like string grouping a chain; NULL=standalone
    daily_token_quota = Column(Integer, default=0, nullable=False)   # 每日 token 限额，0=不限制
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
