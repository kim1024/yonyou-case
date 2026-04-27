from sqlalchemy import Column, Integer, String, Text, DateTime, func, Index
from app.database import Base


class VisitLog(Base):
    __tablename__ = "visit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    endpoint = Column(String)
    method = Column(String)
    ip_address = Column(String)
    user_agent = Column(Text)
    industry = Column(String)
    region = Column(String)
    enterprise = Column(String)
    major = Column(String)
    hour = Column(String)
    request_timestamp = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_visit_logs_timestamp", "request_timestamp"),
        Index("idx_visit_logs_industry", "industry"),
        Index("idx_visit_logs_region", "region"),
    )
