from __future__ import annotations

from datetime import UTC, datetime

import pytest

from src.models.opportunity import Opportunity
from src.models.organization import OrganizationConfig
from src.models.profile import ProfessionalProfile


@pytest.fixture()
def organization() -> OrganizationConfig:
    return OrganizationConfig(
        name="ExampleCo",
        source="greenhouse",
        identifier="example",
        priority="high",
        category="infrastructure",
        region="global",
        tags=["cloud", "developer tools"],
    )


@pytest.fixture()
def profile() -> ProfessionalProfile:
    return ProfessionalProfile(
        expertise=["python", "playwright", "pytest", "automation architecture", "quality engineering", "test strategy"],
        preferred_domains=["infrastructure", "developer tools"],
        target_titles=["staff quality engineer", "senior sdet"],
        excluded_titles=["manual tester", "junior qa"],
    )


@pytest.fixture()
def opportunity() -> Opportunity:
    return Opportunity(
        opportunity_id="opp-1",
        organization="ExampleCo",
        title="Staff Quality Engineer, Automation Architecture",
        location="Remote - United States",
        remote=True,
        description=(
            "Lead quality engineering strategy using Python, Pytest, Playwright, REST APIs, "
            "test strategy, architecture, mentoring, and ownership across Kubernetes services."
        ),
        department="Engineering",
        url="https://example.com/jobs/1",
        compensation=None,
        date_published=datetime(2026, 1, 1, tzinfo=UTC),
        source="greenhouse",
        metadata={"category": "infrastructure", "tags": ["cloud", "developer tools"]},
    )

