from __future__ import annotations

from src.models.opportunity import SourceRecord
from src.models.organization import OrganizationConfig
from src.normalization.normalizer import OpportunityNormalizer


def test_greenhouse_record_normalizes_to_common_opportunity(organization: OrganizationConfig) -> None:
    record = SourceRecord(
        source="greenhouse",
        organization=organization,
        raw={
            "id": 123,
            "title": "Senior SDET",
            "location": {"name": "Remote"},
            "content": "<p>Own API testing with Python and Playwright.</p>",
            "departments": [{"name": "Engineering"}],
            "absolute_url": "https://example.com/jobs/123",
            "first_published": "2026-01-01T00:00:00Z",
        },
    )

    opportunity = OpportunityNormalizer().normalize(record)

    assert opportunity is not None
    assert opportunity.organization == "ExampleCo"
    assert opportunity.title == "Senior SDET"
    assert opportunity.remote is True
    assert opportunity.department == "Engineering"
    assert "Own API testing" in opportunity.description
    assert opportunity.metadata["category"] == "infrastructure"


def test_lever_record_normalizes_categories() -> None:
    organization = OrganizationConfig(name="LeverCo", source="lever", identifier="leverco", category="developer-tools")
    record = SourceRecord(
        source="lever",
        organization=organization,
        raw={
            "id": "abc",
            "text": "Staff Quality Engineer",
            "categories": {"location": "Hybrid", "department": "Engineering", "commitment": "Full-time"},
            "descriptionPlain": "Mentor teams and define quality strategy.",
            "hostedUrl": "https://jobs.lever.co/leverco/abc",
            "createdAt": 1767225600000,
        },
    )

    opportunity = OpportunityNormalizer().normalize(record)

    assert opportunity is not None
    assert opportunity.source == "lever"
    assert opportunity.location == "Hybrid"
    assert opportunity.metadata["commitment"] == "Full-time"


def test_ashby_record_normalizes_department() -> None:
    organization = OrganizationConfig(name="AshbyCo", source="ashby", identifier="ashbyco", category="ai-systems")
    record = SourceRecord(
        source="ashby",
        organization=organization,
        raw={
            "id": "job_1",
            "title": "Quality Architect",
            "location": {"name": "Remote"},
            "department": {"name": "Engineering"},
            "descriptionHtml": "<p>Own AI validation and test strategy.</p>",
            "jobUrl": "https://ashby.example.com/job_1",
        },
    )

    opportunity = OpportunityNormalizer().normalize(record)

    assert opportunity is not None
    assert opportunity.source == "ashby"
    assert opportunity.department == "Engineering"
    assert opportunity.remote is True


def test_unknown_source_is_ignored(organization: OrganizationConfig) -> None:
    record = SourceRecord(source="unknown", organization=organization, raw={"title": "Ignored"})

    assert OpportunityNormalizer().normalize(record) is None
