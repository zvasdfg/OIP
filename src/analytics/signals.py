from __future__ import annotations

from collections import Counter

from src.evaluation.engine import TECH_TERMS
from src.models.opportunity import Opportunity
from src.models.profile import ProfessionalProfile


class MarketSignalAnalyzer:
    def analyze(self, opportunities: list[Opportunity], profile: ProfessionalProfile) -> dict[str, list[tuple[str, int]]]:
        text_by_opportunity = [opportunity.searchable_text for opportunity in opportunities]
        technologies = Counter()
        domains = Counter()
        gaps = Counter()
        profile_terms = profile.normalized_expertise()

        for opportunity, text in zip(opportunities, text_by_opportunity, strict=True):
            for term in TECH_TERMS:
                if term in text:
                    technologies[term] += 1
                    if term not in profile_terms:
                        gaps[term] += 1
            category = str(opportunity.metadata.get("category") or "").lower()
            if category:
                domains[category] += 1
            for tag in opportunity.metadata.get("tags", []):
                domains[str(tag).lower()] += 1

        return {
            "trending_technologies": technologies.most_common(15),
            "trending_domains": domains.most_common(15),
            "skill_gaps": gaps.most_common(15),
        }

