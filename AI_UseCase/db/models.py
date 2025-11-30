from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)

    bookings = relationship("Booking", back_populates="customer")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(String, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    booking_type = Column(String)
    date = Column(String)
    time = Column(String)
    status = Column(String, default="confirmed")
    created_at = Column(DateTime, default=datetime.utcnow)
    extra_info = Column(Text, nullable=True)

    customer = relationship("Customer", back_populates="bookings")


class ConversationHistory(Base):
    __tablename__ = "conversation_history"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    role = Column(String)
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    extra_metadata = Column(Text, nullable=True)
