from sqlalchemy import CheckConstraint, Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from app.database import Base

# Enum for Transaction Type and Category
class TransactionType(PyEnum):
    credit = "credit"
    debit = "debit"
    funding = "funding"
    points_redeemed = "points_redeemed"

class TransactionCategory(PyEnum):
    wallet_funding = "wallet_funding"
    point_usage = "point_usage"
    tour_booking = "tour_booking"

# User Model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    wallets = relationship("Wallet", back_populates="owner", cascade="all, delete")
    points_transactions = relationship("PointsTransaction", back_populates="user", cascade="all, delete")
    tour_transactions = relationship("TourTransaction", back_populates="user", cascade="all, delete")

# Wallet Model
class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    balance = Column(Float, default=0.0)
    currency = Column(String, default="GHS")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="wallets")
    transactions = relationship("Transaction", back_populates="wallet", cascade="all, delete")

    # Ensure balance is never negative
    __table_args__ = (
        CheckConstraint('balance >= 0', name='check_balance_non_negative'),
    )

# Transaction Model
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id"))
    amount = Column(Float)
    transaction_type = Column(Enum(TransactionType), nullable=False)  # Enum for 'credit' or 'debit'
    transaction_category = Column(Enum(TransactionCategory), nullable=False)  # Enum for categorizing
    status = Column(String, default="pending")  # Add status (e.g., 'pending', 'completed')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    wallet = relationship("Wallet", back_populates="transactions")

# PointsTransaction Model
class PointsTransaction(Base):
    __tablename__ = "points_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    activity_type = Column(String)  # 'booking', 'referral', etc.
    details = Column(String, nullable=True)  # Renamed from metadata
    points = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="points_transactions")

# Vendor Model
class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    service_type = Column(String)  # e.g., "tour", "food", etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tours = relationship("Tour", back_populates="vendor")

# Tour Model
class Tour(Base):
    __tablename__ = "tours"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String)
    distance_km = Column(Float)  # Used to calculate points
    price = Column(Float)
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    vendor = relationship("Vendor", back_populates="tours")
    tour_transactions = relationship("TourTransaction", back_populates="tour")

# TourTransaction Model
class TourTransaction(Base):
    __tablename__ = "tour_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    tour_id = Column(Integer, ForeignKey("tours.id"))
    amount_paid = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")  # Add status (e.g., 'completed', 'pending')

    user = relationship("User", back_populates="tour_transactions")
    tour = relationship("Tour", back_populates="tour_transactions")
