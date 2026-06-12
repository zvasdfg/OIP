from __future__ import annotations

from src.evaluation.engine import EvaluationEngine
from src.models.opportunity import Opportunity
from src.models.profile import ProfessionalProfile


def test_evaluation_scores_high_alignment(opportunity: Opportunity, profile: ProfessionalProfile) -> None:
    result = EvaluationEngine().evaluate(opportunity, profile)

    assert result.alignment_score >= 90
    assert "python" in result.matched_expertise
    assert "infrastructure" in result.matched_domains
    assert "kubernetes" in result.gaps


def test_evaluation_caps_excluded_titles(opportunity: Opportunity, profile: ProfessionalProfile) -> None:
    excluded = opportunity.model_copy(update={"title": "Junior QA Analyst"})

    result = EvaluationEngine().evaluate(excluded, profile)

    assert result.alignment_score <= 45

