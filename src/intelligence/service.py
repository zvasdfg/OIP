from __future__ import annotations

from src.models.evaluation import EvaluationResult, IntelligenceInsight
from src.models.opportunity import Opportunity
from src.models.profile import ProfessionalProfile


class IntelligenceService:
    def generate(
        self,
        opportunity: Opportunity,
        evaluation: EvaluationResult,
        profile: ProfessionalProfile,
    ) -> IntelligenceInsight:
        strategic_fit = self._strategic_fit(evaluation.alignment_score)
        priority = self._engagement_priority(evaluation.alignment_score)
        strengths = self._strengths(evaluation)
        gaps = evaluation.gaps[:8]
        analysis = self._analysis(opportunity, evaluation, profile)
        return IntelligenceInsight(
            alignment_score=evaluation.alignment_score,
            strategic_fit=strategic_fit,
            engagement_priority=priority,
            strengths=strengths,
            gaps=gaps,
            analysis=analysis,
        )

    @staticmethod
    def _strategic_fit(score: int) -> str:
        if score >= 90:
            return "high"
        if score >= 75:
            return "strong"
        if score >= 60:
            return "moderate"
        return "low"

    @staticmethod
    def _engagement_priority(score: int) -> str:
        if score >= 90:
            return "recommended"
        if score >= 75:
            return "watchlist"
        if score >= 60:
            return "monitor"
        return "low_priority"

    @staticmethod
    def _strengths(evaluation: EvaluationResult) -> list[str]:
        candidates = [
            *evaluation.matched_expertise,
            *evaluation.matched_domains,
            *evaluation.leadership_signals,
        ]
        seen: set[str] = set()
        strengths: list[str] = []
        for item in candidates:
            if item not in seen:
                strengths.append(item)
                seen.add(item)
        return strengths[:10]

    @staticmethod
    def _analysis(opportunity: Opportunity, evaluation: EvaluationResult, profile: ProfessionalProfile) -> str:
        category = opportunity.metadata.get("category") or "target"
        if evaluation.alignment_score >= 90:
            return (
                f"Excellent alignment with {category}-focused quality engineering needs, "
                "with strong evidence of expertise fit and leadership scope."
            )
        if evaluation.alignment_score >= 75:
            return (
                f"Strong alignment for {profile.target_titles[0] if profile.target_titles else 'target'} positioning, "
                "with enough skill and domain overlap to prioritize active review."
            )
        if evaluation.alignment_score >= 60:
            return "Moderate alignment; monitor for better seniority, domain, or remote-work signals before engagement."
        return "Low alignment against the current profile and should remain a low-priority market signal."

