from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.sql import func
from backend.models.base import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    session_id = Column(String, nullable=True)
    agent = Column(String, nullable=True)
    tool = Column(String, nullable=True)
    execution_id = Column(String, nullable=True)
    status = Column(String, nullable=False)
    duration = Column(Float, nullable=True)
    result_summary = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
