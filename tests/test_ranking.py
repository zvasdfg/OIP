from __future__ import annotations

from src.models.evaluation import OpportunityScore
from src.ranking.engine import RankingEngine


def test_tier_boundaries() -> None:
    ranker = RankingEngine()

    assert ranker.tier_for_score(95) == "A"
    assert ranker.tier_for_score(75) == "B"
    assert ranker.tier_for_score(60) == "C"
    assert ranker.tier_for_score(59) == "D"


def test_rank_orders_by_alignment(opportunity) -> None:
    ranker = RankingEngine()
    lower = opportunity.model_copy(update={"opportunity_id": "low", "title": "Senior SDET"})
    higher = opportunity.model_copy(update={"opportunity_id": "high", "title": "Staff Quality Engineer"})

    ranked = ranker.rank(
        [
            (lower, OpportunityScore(opportunity_id="low", alignment_score=80, tier="B", strategic_fit="strong", engagement_priority="watchlist", criterion_scores={}, analysis="")),
            (higher, OpportunityScore(opportunity_id="high", alignment_score=96, tier="A", strategic_fit="high", engagement_priority="recommended", criterion_scores={}, analysis="")),
        ]
    )

    assert ranked[0][0].opportunity_id == "high"

