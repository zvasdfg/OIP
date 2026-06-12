from __future__ import annotations

from src.models.evaluation import OpportunityScore
from src.models.opportunity import Opportunity


class RankingEngine:
    def tier_for_score(self, score: int) -> str:
        if score >= 90:
            return "A"
        if score >= 75:
            return "B"
        if score >= 60:
            return "C"
        return "D"

    def rank(self, scored_opportunities: list[tuple[Opportunity, OpportunityScore]]) -> list[tuple[Opportunity, OpportunityScore]]:
        return sorted(
            scored_opportunities,
            key=lambda item: (item[1].alignment_score, item[0].date_published or item[0].last_seen_at),
            reverse=True,
        )

