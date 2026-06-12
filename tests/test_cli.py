from __future__ import annotations

import importlib

from typer.testing import CliRunner


class FakePipeline:
    def collect(self):
        return {"opportunities": 1}

    def evaluate(self, limit=None):
        return {"scores": 1, "limit": limit}

    def rank(self, limit=25):
        from src.models.evaluation import OpportunityScore
        from src.models.opportunity import Opportunity

        opportunity = Opportunity(
            opportunity_id="opp-1",
            organization="ExampleCo",
            title="Staff Quality Engineer",
            location="Remote",
            remote=True,
            description="Python quality engineering.",
            source="greenhouse",
            metadata={"category": "infrastructure"},
        )
        score = OpportunityScore(
            opportunity_id=opportunity.opportunity_id,
            alignment_score=91,
            tier="A",
            strategic_fit="high",
            engagement_priority="recommended",
            criterion_scores={},
            analysis="",
        )
        return [(opportunity, score)]

    def report(self, limit=50):
        return "reports/daily_intelligence_report.html"

    def notify(self, limit=10):
        return {"email": False, "telegram": False}

    def run_once(self):
        return {"report": "reports/daily_intelligence_report.html"}


def test_cli_commands(monkeypatch) -> None:
    cli_module = importlib.import_module("src.cli.app")
    monkeypatch.setattr(cli_module, "_pipeline", lambda: FakePipeline())
    runner = CliRunner()

    assert runner.invoke(cli_module.app, ["collect"]).exit_code == 0
    assert runner.invoke(cli_module.app, ["evaluate", "--limit", "10"]).exit_code == 0
    rank_result = runner.invoke(cli_module.app, ["rank", "--limit", "1"])
    assert rank_result.exit_code == 0
    assert "ExampleCo" in rank_result.output
    assert runner.invoke(cli_module.app, ["report"]).exit_code == 0
    assert runner.invoke(cli_module.app, ["notify"]).exit_code == 0
    assert runner.invoke(cli_module.app, ["run"]).exit_code == 0
