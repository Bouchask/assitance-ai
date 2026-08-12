from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.models.base import Base

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String, unique=True, index=True, nullable=False)
    quote_id = Column(Integer, ForeignKey("quotes.id"), nullable=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    status = Column(String, default="DRAFT") # DRAFT, SENT, PAID, CANCELLED
    subtotal = Column(Float, default=0.0)
    tax_total = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    is_paid = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    due_date = Column(DateTime(timezone=True), nullable=True)

    client = relationship("Client")
    quote = relationship("Quote")
    items = relationship("InvoiceItem", back_populates="invoice")

class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    quantity = Column(Float, default=1.0)
    unit_price = Column(Float, nullable=False)
    tax_rate = Column(Float, default=20.0)
    discount = Column(Float, default=0.0)
    
    invoice = relationship("Invoice", back_populates="items")
    service = relationship("Service")
