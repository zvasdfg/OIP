from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.storage.database import Base


def utcnow() -> datetime:
    return datetime.now(UTC)


class OrganizationORM(Base):
    __tablename__ = "organizations"
    __table_args__ = (UniqueConstraint("source", "identifier", name="uq_organizations_source_identifier"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    identifier: Mapped[str] = mapped_column(String(255), nullable=False)
    priority: Mapped[str] = mapped_column(String(32), nullable=False, default="medium")
    category: Mapped[str | None] = mapped_column(String(128))
    region: Mapped[str | None] = mapped_column(String(128))
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class OpportunityORM(Base):
    __tablename__ = "opportunities"

    opportunity_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    location: Mapped[str | None] = mapped_column(String(512))
    remote: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    department: Mapped[str | None] = mapped_column(String(255))
    url: Mapped[str | None] = mapped_column(Text)
    compensation: Mapped[str | None] = mapped_column(Text)
    date_published: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    source: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    metadata_json: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class OpportunityScoreORM(Base):
    __tablename__ = "opportunity_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    opportunity_id: Mapped[str] = mapped_column(ForeignKey("opportunities.opportunity_id"), index=True, nullable=False)
    alignment_score: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    tier: Mapped[str] = mapped_column(String(1), nullable=False, index=True)
    strategic_fit: Mapped[str] = mapped_column(String(64), nullable=False)
    engagement_priority: Mapped[str] = mapped_column(String(64), nullable=False)
    criterion_scores: Mapped[dict] = mapped_column(JSON, default=dict)
    strengths: Mapped[list[str]] = mapped_column(JSON, default=list)
    gaps: Mapped[list[str]] = mapped_column(JSON, default=list)
    analysis: Mapped[str] = mapped_column(Text, default="")
    evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class OpportunitySnapshotORM(Base):
    __tablename__ = "opportunity_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    opportunity_id: Mapped[str] = mapped_column(ForeignKey("opportunities.opportunity_id"), index=True, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    snapshot: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class EngagementORM(Base):
    __tablename__ = "engagements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    opportunity_id: Mapped[str] = mapped_column(ForeignKey("opportunities.opportunity_id"), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(64), default="Discovered", index=True)
    notes: Mapped[str | None] = mapped_column(Text)
    outcome: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class BookmarkORM(Base):
    __tablename__ = "bookmarks"
    __table_args__ = (UniqueConstraint("opportunity_id", name="uq_bookmarks_opportunity_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    opportunity_id: Mapped[str] = mapped_column(ForeignKey("opportunities.opportunity_id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class AnalyticsORM(Base):
    __tablename__ = "analytics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    value: Mapped[float | None] = mapped_column(Float)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)


Index("ix_scores_latest_lookup", OpportunityScoreORM.opportunity_id, OpportunityScoreORM.evaluated_at)

