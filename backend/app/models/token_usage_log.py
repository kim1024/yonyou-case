"""Token 消耗记录表。"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, func
from app.database import Base


class TokenUsageLog(Base):
    """Token 消耗记录"""
    __tablename__ = "token_usage_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    llm_config_id = Column(Integer, ForeignKey("llm_configs.id"), nullable=False)  # 关联模型配置
    model = Column(String(100), nullable=False)               # 实际调用的模型名
    prompt_tokens = Column(Integer, default=0)                # 输入 token 数
    completion_tokens = Column(Integer, default=0)            # 输出 token 数
    total_tokens = Column(Integer, default=0)                 # 总 token 数
    request_timestamp = Column(DateTime, server_default=func.now())  # 请求时间

    __table_args__ = (
        Index("idx_token_usage_logs_timestamp", "request_timestamp"),
        Index("idx_token_usage_logs_model", "model"),
        Index("idx_token_usage_logs_llm_config_id", "llm_config_id"),
    )
