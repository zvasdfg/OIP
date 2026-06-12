from __future__ import annotations

import logging
from pathlib import Path

from src.config.loader import ConfigLoader
from src.config.settings import Settings
from src.evaluation.engine import EvaluationEngine
from src.intelligence.service import IntelligenceService
from src.models.evaluation import OpportunityScore
from src.models.opportunity import Opportunity, SourceRecord
from src.normalization.normalizer import OpportunityNormalizer
from src.notifications.service import NotificationService
from src.ranking.engine import RankingEngine
from src.reporting.report_service import ReportService
from src.sources.factory import SourceFactory
from src.storage.database import Database
from src.storage.repositories import OpportunityRepository

logger = logging.getLogger(__name__)


class OpportunityPipeline:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.loader = ConfigLoader(settings.organizations_path, settings.profile_path)
        self.database = Database(settings.database_url)
        self.database.init_schema()
        self.repository = OpportunityRepository(self.database)
        self.source_factory = SourceFactory(settings)
        self.normalizer = OpportunityNormalizer()
        self.evaluator = EvaluationEngine()
        self.intelligence = IntelligenceService()
        self.ranker = RankingEngine()
        self.reporter = ReportService(settings.reports_dir)
        self.notifier = NotificationService(settings)

    def collect(self) -> dict[str, int]:
        organizations = self.loader.load_organizations()
        self.repository.save_organizations(organizations)
        records: list[SourceRecord] = []
        for organization in organizations:
            try:
                source = self.source_factory.get(organization.source)
                records.extend(source.collect(organization))
            except NotImplementedError:
                logger.info(
                    "Skipping organization with source abstraction only",
                    extra={"organization": organization.name, "source": organization.source.value},
                )
            except Exception as exc:
                logger.exception(
                    "Unexpected source collection failure",
                    extra={"organization": organization.name, "source": organization.source.value, "error": str(exc)},
                )
        opportunities = self.normalizer.normalize_many(records)
        saved = self.repository.save_opportunities(opportunities)
        logger.info(
            "Collection completed",
            extra={"organizations": len(organizations), "records": len(records), "opportunities": saved},
        )
        return {"organizations": len(organizations), "records": len(records), "opportunities": saved}

    def evaluate(self, limit: int | None = None) -> dict[str, int]:
        profile = self.loader.load_profile()
        opportunities = self.repository.list_opportunities(limit=limit)
        scores = [self._score_opportunity(opportunity, profile) for opportunity in opportunities]
        saved = self.repository.save_scores(scores)
        logger.info("Evaluation completed", extra={"opportunities": len(opportunities), "scores": saved})
        return {"opportunities": len(opportunities), "scores": saved}

    def rank(self, limit: int = 50) -> list[tuple[Opportunity, OpportunityScore]]:
        ranked = self.repository.ranked_opportunities(limit=limit)
        logger.info("Ranking completed", extra={"ranked": len(ranked)})
        return ranked

    def report(self, limit: int = 50) -> Path:
        profile = self.loader.load_profile()
        ranked = self.rank(limit=limit)
        path = self.reporter.generate_daily_report(ranked, profile)
        logger.info("Report generated", extra={"path": str(path)})
        return path

    def notify(self, limit: int = 10) -> dict[str, bool]:
        ranked = self.rank(limit=limit)
        return self.notifier.send_daily(ranked)

    def run_once(self) -> dict[str, object]:
        collection = self.collect()
        evaluation = self.evaluate()
        report_path = self.report()
        notification = self.notify()
        return {
            "collection": collection,
            "evaluation": evaluation,
            "report": str(report_path),
            "notification": notification,
        }

    def _score_opportunity(self, opportunity: Opportunity, profile) -> OpportunityScore:
        evaluation = self.evaluator.evaluate(opportunity, profile)
        insight = self.intelligence.generate(opportunity, evaluation, profile)
        return OpportunityScore(
            opportunity_id=opportunity.opportunity_id,
            alignment_score=insight.alignment_score,
            tier=self.ranker.tier_for_score(insight.alignment_score),
            strategic_fit=insight.strategic_fit,
            engagement_priority=insight.engagement_priority,
            criterion_scores=evaluation.criterion_scores,
            strengths=insight.strengths,
            gaps=insight.gaps,
            analysis=insight.analysis,
            evaluated_at=evaluation.evaluated_at,
        )

