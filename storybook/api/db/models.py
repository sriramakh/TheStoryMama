"""SQLAlchemy ORM models for TheStoryMama."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # NULL for OAuth-only
    name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    provider = Column(String(50), default="credentials")  # credentials, google
    provider_id = Column(String(255), nullable=True)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    stories = relationship("Story", back_populates="owner")
    orders = relationship("Order", back_populates="user")
    credits = relationship("Credit", back_populates="user")
    generation_jobs = relationship("GenerationJob", back_populates="user")


class Story(Base):
    __tablename__ = "stories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    folder_name = Column(String(255), unique=True, nullable=False)
    title = Column(String(500), nullable=False)
    setting = Column(Text, nullable=True)
    art_style = Column(Text, nullable=True)
    moral = Column(Text, nullable=True)
    instagram_caption = Column(Text, nullable=True)
    animation_style = Column(String(50), nullable=True)
    story_data = Column(JSONB, nullable=False)  # Full story JSON
    is_public = Column(Boolean, default=False, index=True)
    category = Column(String(100), nullable=True, index=True)
    tags = Column(ARRAY(String(100)), nullable=True)
    cover_image_url = Column(String(500), nullable=True)
    scene_count = Column(Integer, nullable=True)
    owner_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    owner = relationship("User", back_populates="stories")

    __table_args__ = (
        Index("idx_stories_public_category", "is_public", "category"),
    )


class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    stripe_session_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    plan_type = Column(String(50), nullable=False)  # pack_5, monthly_10, yearly_15
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String(3), default="usd")
    status = Column(String(50), default="pending")  # pending, paid, refunded, cancelled
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    user = relationship("User", back_populates="orders")
    credits = relationship("Credit", back_populates="order")


class Credit(Base):
    __tablename__ = "credits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    total = Column(Integer, nullable=False, default=0)
    used = Column(Integer, nullable=False, default=0)
    order_id = Column(
        UUID(as_uuid=True), ForeignKey("orders.id"), nullable=True
    )
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    user = relationship("User", back_populates="credits")
    order = relationship("Order", back_populates="credits")


class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    story_id = Column(
        UUID(as_uuid=True), ForeignKey("stories.id"), nullable=True
    )
    status = Column(String(50), nullable=False, default="queued")
    progress = Column(Float, default=0.0)
    message = Column(Text, nullable=True)
    request_data = Column(JSONB, nullable=True)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="generation_jobs")
    story = relationship("Story")
