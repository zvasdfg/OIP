from __future__ import annotations

from src.config.settings import Settings
from src.models.opportunity import SourceRecord
from src.services.pipeline import OpportunityPipeline


class FakeSourceFactory:
    def get(self, source_type):
        return self

    def collect(self, organization):
        return [
            SourceRecord(
                source="greenhouse",
                organization=organization,
                raw={
                    "id": 1,
                    "title": "Staff Quality Engineer",
                    "location": {"name": "Remote"},
                    "content": "Python Playwright quality engineering strategy architecture mentoring.",
                    "departments": [{"name": "Engineering"}],
                    "absolute_url": "https://example.com/jobs/1",
                },
            )
        ]


class FakeNotifier:
    def send_daily(self, ranked):
        return {"email": True, "telegram": False}


def _write_config(tmp_path) -> tuple:
    organizations_path = tmp_path / "organizations.yaml"
    profile_path = tmp_path / "profile.yaml"
    organizations_path.write_text(
        """
- name: ExampleCo
  source: greenhouse
  identifier: example
  priority: high
  category: infrastructure
  tags: [developer tools]
""",
        encoding="utf-8",
    )
    profile_path.write_text(
        """
expertise: [python, playwright, quality engineering]
preferred_domains: [infrastructure, developer tools]
target_titles: [staff quality engineer]
excluded_titles: [manual tester]
""",
        encoding="utf-8",
    )
    return organizations_path, profile_path


def test_pipeline_runs_full_workflow(tmp_path) -> None:
    organizations_path, profile_path = _write_config(tmp_path)
    settings = Settings(
        organizations_path=organizations_path,
        profile_path=profile_path,
        database_url=f"sqlite:///{tmp_path / 'oip.sqlite3'}",
        reports_dir=tmp_path / "reports",
    )
    pipeline = OpportunityPipeline(settings)
    pipeline.source_factory = FakeSourceFactory()
    pipeline.notifier = FakeNotifier()

    result = pipeline.run_once()

    assert result["collection"]["opportunities"] == 1
    assert result["evaluation"]["scores"] == 1
    assert (tmp_path / "reports" / "daily_intelligence_report.html").exists()
    assert result["notification"] == {"email": True, "telegram": False}

