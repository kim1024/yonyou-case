"""模型降级链阈值配置表。"""

from sqlalchemy import Column, Integer, DateTime, ForeignKey, func
from app.database import Base


class ModelFallbackSetting(Base):
    """降级链阈值设置 —— 每条链（由 primary LLMConfig 标识）一行。"""
    __tablename__ = "model_fallback_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    primary_llm_config_id = Column(Integer, ForeignKey("llm_configs.id"), unique=True, nullable=False)
    failure_threshold = Column(Integer, default=3)      # 连续失败次数阈值
    timeout_seconds = Column(Integer, default=5)        # 单次请求超时阈值（秒）
    cooldown_seconds = Column(Integer, default=300)     # 降级冷却时间（秒），之后重新尝试 primary
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    @property
    def timeout_threshold(self) -> int:
        """兼容旧字段名。"""
        return self.timeout_seconds

    @timeout_threshold.setter
    def timeout_threshold(self, value: int):
        self.timeout_seconds = value
