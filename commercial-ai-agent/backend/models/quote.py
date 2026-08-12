from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.models.base import Base

class Quote(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)
    quote_number = Column(String, unique=True, index=True, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    status = Column(String, default="DRAFT") # DRAFT, SENT, ACCEPTED, REJECTED, INVOICED
    subtotal = Column(Float, default=0.0)
    tax_total = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    valid_until = Column(DateTime(timezone=True), nullable=True)

    client = relationship("Client")
    items = relationship("QuoteItem", back_populates="quote")

class QuoteItem(Base):
    __tablename__ = "quote_items"

    id = Column(Integer, primary_key=True, index=True)
    quote_id = Column(Integer, ForeignKey("quotes.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    quantity = Column(Float, default=1.0)
    unit_price = Column(Float, nullable=False)
    tax_rate = Column(Float, default=20.0)
    discount = Column(Float, default=0.0)
    
    quote = relationship("Quote", back_populates="items")
    service = relationship("Service")
