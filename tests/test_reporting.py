from __future__ import annotations

from src.models.evaluation import OpportunityScore
from src.models.opportunity import Opportunity
from src.models.profile import ProfessionalProfile
from src.reporting.report_service import ReportService


def test_daily_report_is_rendered(tmp_path, opportunity: Opportunity, profile: ProfessionalProfile) -> None:
    score = OpportunityScore(
        opportunity_id=opportunity.opportunity_id,
        alignment_score=96,
        tier="A",
        strategic_fit="high",
        engagement_priority="recommended",
        criterion_scores={"strategic_alignment": 1.0},
        strengths=["python", "quality engineering"],
        gaps=["kubernetes"],
        analysis="Excellent alignment.",
    )

    path = ReportService(tmp_path).generate_daily_report([(opportunity, score)], profile)

    assert path.exists()
    rendered = path.read_text(encoding="utf-8")
    assert "Daily Opportunity Intelligence Report" in rendered
    assert "ExampleCo" in rendered
    assert "Priority Opportunities" in rendered

