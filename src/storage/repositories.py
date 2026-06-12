from __future__ import annotations

import hashlib
import json
from collections import defaultdict

from sqlalchemy import select

from src.models.evaluation import OpportunityScore
from src.models.opportunity import Opportunity
from src.models.organization import OrganizationConfig
from src.storage.database import Database
from src.storage.schema import (
    AnalyticsORM,
    EngagementORM,
    OpportunityORM,
    OpportunityScoreORM,
    OpportunitySnapshotORM,
    OrganizationORM,
)


class OpportunityRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def save_organizations(self, organizations: list[OrganizationConfig]) -> int:
        with self.database.session_factory() as session:
            count = 0
            for organization in organizations:
                existing = session.execute(
                    select(OrganizationORM).where(
                        OrganizationORM.source == organization.source.value,
                        OrganizationORM.identifier == organization.identifier,
                    )
                ).scalar_one_or_none()
                if existing is None:
                    session.add(
                        OrganizationORM(
                            name=organization.name,
                            source=organization.source.value,
                            identifier=organization.identifier,
                            priority=organization.priority,
                            category=organization.category,
                            region=organization.region,
                            tags=organization.tags,
                        )
                    )
                else:
                    existing.name = organization.name
                    existing.priority = organization.priority
                    existing.category = organization.category
                    existing.region = organization.region
                    existing.tags = organization.tags
                count += 1
            session.commit()
            return count

    def save_opportunities(self, opportunities: list[Opportunity]) -> int:
        with self.database.session_factory() as session:
            saved = 0
            for opportunity in opportunities:
                payload = opportunity.model_dump(mode="json")
                content_hash = _content_hash(payload)
                existing = session.get(OpportunityORM, opportunity.opportunity_id)
                if existing is None:
                    existing = OpportunityORM(
                        opportunity_id=opportunity.opportunity_id,
                        organization=opportunity.organization,
                        title=opportunity.title,
                        location=opportunity.location,
                        remote=opportunity.remote,
                        description=opportunity.description,
                        department=opportunity.department,
                        url=str(opportunity.url) if opportunity.url else None,
                        compensation=opportunity.compensation,
                        date_published=opportunity.date_published,
                        source=opportunity.source,
                        metadata_json=opportunity.metadata,
                        content_hash=content_hash,
                        first_seen_at=opportunity.first_seen_at,
                        last_seen_at=opportunity.last_seen_at,
                    )
                    session.add(existing)
                    session.add(
                        OpportunitySnapshotORM(
                            opportunity_id=opportunity.opportunity_id,
                            content_hash=content_hash,
                            snapshot=payload,
                        )
                    )
                    saved += 1
                    continue

                existing.organization = opportunity.organization
                existing.title = opportunity.title
                existing.location = opportunity.location
                existing.remote = opportunity.remote
                existing.description = opportunity.description
                existing.department = opportunity.department
                existing.url = str(opportunity.url) if opportunity.url else None
                existing.compensation = opportunity.compensation
                existing.date_published = opportunity.date_published
                existing.source = opportunity.source
                existing.metadata_json = opportunity.metadata
                if existing.content_hash != content_hash:
                    existing.content_hash = content_hash
                    session.add(
                        OpportunitySnapshotORM(
                            opportunity_id=opportunity.opportunity_id,
                            content_hash=content_hash,
                            snapshot=payload,
                        )
                    )
                saved += 1
            session.commit()
            return saved

    def list_opportunities(self, limit: int | None = None) -> list[Opportunity]:
        with self.database.session_factory() as session:
            statement = select(OpportunityORM).order_by(OpportunityORM.last_seen_at.desc())
            if limit:
                statement = statement.limit(limit)
            rows = session.execute(statement).scalars().all()
            return [_to_opportunity(row) for row in rows]

    def save_scores(self, scores: list[OpportunityScore]) -> int:
        with self.database.session_factory() as session:
            for score in scores:
                session.add(
                    OpportunityScoreORM(
                        opportunity_id=score.opportunity_id,
                        alignment_score=score.alignment_score,
                        tier=score.tier,
                        strategic_fit=score.strategic_fit,
                        engagement_priority=score.engagement_priority,
                        criterion_scores=score.criterion_scores,
                        strengths=score.strengths,
                        gaps=score.gaps,
                        analysis=score.analysis,
                        evaluated_at=score.evaluated_at,
                    )
                )
            session.commit()
            return len(scores)

    def latest_scores(self, limit: int | None = None) -> dict[str, OpportunityScore]:
        with self.database.session_factory() as session:
            rows = session.execute(select(OpportunityScoreORM).order_by(OpportunityScoreORM.evaluated_at.desc())).scalars()
            latest: dict[str, OpportunityScoreORM] = {}
            for row in rows:
                latest.setdefault(row.opportunity_id, row)
                if limit and len(latest) >= limit:
                    break
            return {opportunity_id: _to_score(row) for opportunity_id, row in latest.items()}

    def ranked_opportunities(self, limit: int = 50) -> list[tuple[Opportunity, OpportunityScore]]:
        opportunities = {opportunity.opportunity_id: opportunity for opportunity in self.list_opportunities()}
        scores = self.latest_scores()
        ranked = [
            (opportunities[opportunity_id], score)
            for opportunity_id, score in scores.items()
            if opportunity_id in opportunities
        ]
        ranked.sort(key=lambda item: item[1].alignment_score, reverse=True)
        return ranked[:limit]

    def save_analytics(self, name: str, payload: dict, value: float | None = None) -> None:
        with self.database.session_factory() as session:
            session.add(AnalyticsORM(name=name, value=value, payload=payload))
            session.commit()

    def engagement_summary(self) -> dict[str, int]:
        with self.database.session_factory() as session:
            rows = session.execute(select(EngagementORM.status)).scalars().all()
        summary: dict[str, int] = defaultdict(int)
        for status in rows:
            summary[status] += 1
        return dict(summary)


def _to_opportunity(row: OpportunityORM) -> Opportunity:
    return Opportunity(
        opportunity_id=row.opportunity_id,
        organization=row.organization,
        title=row.title,
        location=row.location,
        remote=row.remote,
        description=row.description,
        department=row.department,
        url=row.url,
        compensation=row.compensation,
        date_published=row.date_published,
        source=row.source,
        metadata=row.metadata_json or {},
        first_seen_at=row.first_seen_at,
        last_seen_at=row.last_seen_at,
    )


def _to_score(row: OpportunityScoreORM) -> OpportunityScore:
    return OpportunityScore(
        opportunity_id=row.opportunity_id,
        alignment_score=row.alignment_score,
        tier=row.tier,
        strategic_fit=row.strategic_fit,
        engagement_priority=row.engagement_priority,
        criterion_scores=row.criterion_scores or {},
        strengths=row.strengths or [],
        gaps=row.gaps or [],
        analysis=row.analysis,
        evaluated_at=row.evaluated_at,
    )


def _content_hash(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode("utf-8")).hexdigest()

