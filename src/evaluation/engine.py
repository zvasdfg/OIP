from __future__ import annotations

import re

from src.models.evaluation import EvaluationResult
from src.models.opportunity import Opportunity
from src.models.profile import ProfessionalProfile

LEADERSHIP_TERMS = {
    "architecture",
    "strategy",
    "mentoring",
    "mentor",
    "technical leadership",
    "leadership",
    "ownership",
    "roadmap",
    "influence",
    "principal",
    "staff",
}

TECH_TERMS = {
    "aws",
    "azure",
    "gcp",
    "kubernetes",
    "docker",
    "terraform",
    "go",
    "java",
    "python",
    "typescript",
    "playwright",
    "selenium",
    "pytest",
    "cypress",
    "graphql",
    "rest",
    "soap",
    "ci/cd",
    "linux",
    "security",
    "ai",
    "machine learning",
}


class EvaluationEngine:
    weights = {
        "strategic_alignment": 0.30,
        "expertise_alignment": 0.30,
        "domain_alignment": 0.15,
        "work_model_alignment": 0.10,
        "leadership_alignment": 0.15,
    }

    def evaluate(self, opportunity: Opportunity, profile: ProfessionalProfile) -> EvaluationResult:
        text = opportunity.searchable_text
        title_text = opportunity.title.lower()
        excluded = [term for term in profile.excluded_titles if _contains_phrase(title_text, term)]

        strategic_score = 0.0 if excluded else self._strategic_alignment(opportunity, profile)
        matched_expertise = sorted(term for term in profile.normalized_expertise() if _contains_phrase(text, term))
        expertise_score = self._ratio_score(len(matched_expertise), max(len(profile.expertise), 1), saturation=0.45)
        matched_domains = self._matched_domains(opportunity, profile, text)
        domain_score = self._domain_score(matched_domains, profile)
        work_model_score = self._work_model_score(opportunity, profile)
        leadership_signals = sorted(term for term in LEADERSHIP_TERMS if _contains_phrase(text, term))
        leadership_score = self._ratio_score(len(leadership_signals), 6, saturation=1.0)

        criterion_scores = {
            "strategic_alignment": strategic_score,
            "expertise_alignment": expertise_score,
            "domain_alignment": domain_score,
            "work_model_alignment": work_model_score,
            "leadership_alignment": leadership_score,
        }
        weighted = sum(criterion_scores[name] * weight for name, weight in self.weights.items()) * 100
        alignment_score = int(round(weighted))
        if excluded:
            alignment_score = min(alignment_score, 45)

        requested_terms = sorted(term for term in TECH_TERMS if _contains_phrase(text, term))
        gaps = [term for term in requested_terms if term not in profile.normalized_expertise()]

        return EvaluationResult(
            opportunity_id=opportunity.opportunity_id,
            alignment_score=max(0, min(100, alignment_score)),
            criterion_scores=criterion_scores,
            matched_expertise=matched_expertise,
            matched_domains=matched_domains,
            leadership_signals=leadership_signals,
            gaps=gaps,
        )

    def _strategic_alignment(self, opportunity: Opportunity, profile: ProfessionalProfile) -> float:
        title = opportunity.title.lower()
        if any(_contains_phrase(title, target) for target in profile.target_titles):
            return 1.0
        high_signal_terms = ["staff", "principal", "senior", "architect", "quality", "sdet", "automation", "test"]
        matches = sum(1 for term in high_signal_terms if _contains_phrase(title, term))
        return min(1.0, matches / 4)

    def _matched_domains(self, opportunity: Opportunity, profile: ProfessionalProfile, text: str) -> list[str]:
        values = {
            str(opportunity.metadata.get("category") or "").lower(),
            *(str(tag).lower() for tag in opportunity.metadata.get("tags", [])),
        }
        matched = set()
        for domain in profile.normalized_domains():
            if _contains_phrase(text, domain) or any(_contains_phrase(value, domain) for value in values):
                matched.add(domain)
        return sorted(matched)

    def _domain_score(self, matched_domains: list[str], profile: ProfessionalProfile) -> float:
        if not profile.preferred_domains:
            return 0.5
        return self._ratio_score(len(matched_domains), max(len(profile.preferred_domains), 1), saturation=0.5)

    @staticmethod
    def _work_model_score(opportunity: Opportunity, profile: ProfessionalProfile) -> float:
        location = (opportunity.location or "").lower()
        preferred = {item.lower() for item in profile.preferred_work_models}
        if opportunity.remote and ("remote" in preferred or "distributed" in preferred):
            return 1.0
        if "hybrid" in location and "hybrid" in preferred:
            return 0.75
        if any(term in location for term in ["remote", "distributed", "anywhere"]):
            return 0.9
        return 0.35

    @staticmethod
    def _ratio_score(count: int, denominator: int, saturation: float) -> float:
        if denominator <= 0:
            return 0.0
        return max(0.0, min(1.0, (count / denominator) / saturation))


def _contains_phrase(text: str, phrase: str) -> bool:
    normalized = phrase.strip().lower()
    if not normalized:
        return False
    escaped = re.escape(normalized).replace(r"\ ", r"\s+")
    return re.search(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", text) is not None

