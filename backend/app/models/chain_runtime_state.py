"""Chain runtime state — persisted to DB for multi-process safety."""

from sqlalchemy import Column, String, Integer, Float, DateTime, func

from app.database import Base


class ChainRuntimeState(Base):
    """Runtime state for a single chain group, shared across all workers."""

    __tablename__ = "chain_runtime_states"

    group_id = Column(String(50), primary_key=True)
    current_config_id = Column(Integer, nullable=True)
    failure_count = Column(Integer, nullable=False, default=0)
    timeout_count = Column(Integer, nullable=False, default=0)
    cooling_until = Column(Float, nullable=False, default=0.0)  # epoch timestamp
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
