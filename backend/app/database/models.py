"""
Database Models for FraudLens AI.
Defines Scan records, detailed evidence JSON, and assistant chat conversations.
Compatible with both PostgreSQL and SQLite.
"""

import datetime
import uuid
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class ScanRecord(Base):
    __tablename__ = "scans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    url = Column(String(2048), nullable=False, index=True)
    normalized_url = Column(String(2048), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), index=True)

    # Risk Assessment
    risk_level = Column(String(32), nullable=False, index=True)  # LOW, MEDIUM, HIGH, INCONCLUSIVE
    risk_score = Column(Integer, nullable=False, index=True)     # 0 to 100
    model_score = Column(Float, nullable=True)                  # 0.0 to 1.0 (phishing probability)
    model_version = Column(String(64), nullable=True)
    model_type = Column(String(64), nullable=True)
    is_phishing_predicted = Column(Boolean, nullable=True)

    # Detailed Structured Evidence & Explanations
    features = Column(JSON, nullable=True)
    feature_explanations = Column(JSON, nullable=True)
    indicators = Column(JSON, nullable=True)
    recommendations = Column(JSON, nullable=True)
    domain_intel = Column(JSON, nullable=True)
    threat_intel = Column(JSON, nullable=True)
    plain_explanation = Column(Text, nullable=True)

    # Processing metadata
    status = Column(String(32), default="completed", index=True)  # completed, failed, pending
    error_message = Column(Text, nullable=True)
    is_sample_seed = Column(Boolean, default=False)

    # Relationships
    messages = relationship("ChatMessageRecord", back_populates="scan", cascade="all, delete-orphan")

class ChatMessageRecord(Base):
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    scan_id = Column(String(36), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(16), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    citations = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    # Relationship
    scan = relationship("ScanRecord", back_populates="messages")
