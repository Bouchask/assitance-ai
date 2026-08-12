from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.models.base import Base

class Proposal(Base):
    __tablename__ = "proposals"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    status = Column(String, default="DRAFT") # DRAFT, SENT, ACCEPTED, REJECTED
    total_amount = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    client = relationship("Client")
    items = relationship("ProposalItem", back_populates="proposal")

class ProposalItem(Base):
    __tablename__ = "proposal_items"

    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(Integer, ForeignKey("proposals.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    quantity = Column(Float, default=1.0)
    unit_price = Column(Float, nullable=False)
    discount = Column(Float, default=0.0)
    
    proposal = relationship("Proposal", back_populates="items")
    service = relationship("Service")
