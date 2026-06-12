from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.analytics.signals import MarketSignalAnalyzer
from src.models.evaluation import OpportunityScore
from src.models.opportunity import Opportunity
from src.models.profile import ProfessionalProfile


class ReportService:
    def __init__(self, reports_dir: Path) -> None:
        self.reports_dir = reports_dir
        template_dir = Path(__file__).resolve().parent / "templates"
        self.environment = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(enabled_extensions=("html", "xml")),
        )

    def generate_daily_report(
        self,
        ranked_opportunities: list[tuple[Opportunity, OpportunityScore]],
        profile: ProfessionalProfile,
        output_path: Path | None = None,
    ) -> Path:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        output = output_path or self.reports_dir / "daily_intelligence_report.html"
        opportunities = [opportunity for opportunity, _ in ranked_opportunities]
        signals = MarketSignalAnalyzer().analyze(opportunities, profile)
        high_value = [item for item in ranked_opportunities if item[1].alignment_score >= 75]
        template = self.environment.get_template("daily_report.html.j2")
        rendered = template.render(
            generated_at=datetime.now(UTC),
            ranked_opportunities=ranked_opportunities[:25],
            high_value=high_value,
            signals=signals,
            profile=profile,
            recommendations=self._recommendations(high_value, signals),
        )
        output.write_text(rendered, encoding="utf-8")
        return output

    @staticmethod
    def _recommendations(
        high_value: list[tuple[Opportunity, OpportunityScore]],
        signals: dict[str, list[tuple[str, int]]],
    ) -> list[str]:
        recommendations: list[str] = []
        if high_value:
            recommendations.append(f"Prioritize outreach for the top {min(len(high_value), 5)} Tier A/B opportunities.")
        top_gap = signals.get("skill_gaps", [])[:1]
        if top_gap:
            recommendations.append(f"Address recurring market demand for {top_gap[0][0]} in profile materials.")
        top_domain = signals.get("trending_domains", [])[:1]
        if top_domain:
            recommendations.append(f"Monitor {top_domain[0][0]} organizations for repeat senior quality roles.")
        if not recommendations:
            recommendations.append("Continue collection to build enough market volume for stronger trend analysis.")
        return recommendations

