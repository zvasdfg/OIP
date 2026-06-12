from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class EvaluationResult(BaseModel):
    opportunity_id: str
    alignment_score: int
    criterion_scores: dict[str, float]
    matched_expertise: list[str] = Field(default_factory=list)
    matched_domains: list[str] = Field(default_factory=list)
    leadership_signals: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class IntelligenceInsight(BaseModel):
    alignment_score: int
    strategic_fit: str
    engagement_priority: str
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    analysis: str


class OpportunityScore(BaseModel):
    opportunity_id: str
    alignment_score: int
    tier: str
    strategic_fit: str
    engagement_priority: str
    criterion_scores: dict[str, float]
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    analysis: str
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

