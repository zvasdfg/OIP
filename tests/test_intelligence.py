from __future__ import annotations

from src.evaluation.engine import EvaluationEngine
from src.intelligence.service import IntelligenceService
from src.models.opportunity import Opportunity
from src.models.profile import ProfessionalProfile


def test_intelligence_generates_contextual_insight(opportunity: Opportunity, profile: ProfessionalProfile) -> None:
    evaluation = EvaluationEngine().evaluate(opportunity, profile)

    insight = IntelligenceService().generate(opportunity, evaluation, profile)

    assert insight.alignment_score == evaluation.alignment_score
    assert insight.engagement_priority == "recommended"
    assert "python" in insight.strengths
    assert "kubernetes" in insight.gaps
    assert "Excellent alignment" in insight.analysis


def test_intelligence_priority_thresholds(opportunity: Opportunity, profile: ProfessionalProfile) -> None:
    service = IntelligenceService()
    evaluation = EvaluationEngine().evaluate(opportunity, profile)

    for score, expected in [(80, "watchlist"), (65, "monitor"), (40, "low_priority")]:
        adjusted = evaluation.model_copy(update={"alignment_score": score})
        insight = service.generate(opportunity, adjusted, profile)
        assert insight.engagement_priority == expected
