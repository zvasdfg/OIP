from __future__ import annotations

from src.config.settings import Settings
from src.models.organization import OrganizationConfig
from src.sources.ashby import AshbySource
from src.sources.factory import SourceFactory
from src.sources.future import FutureSource
from src.sources.greenhouse import GreenhouseSource
from src.sources.lever import LeverSource


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self, payload):
        self.payload = payload
        self.last_url = ""

    def get(self, url: str, timeout: int):
        self.last_url = url
        return FakeResponse(self.payload)


def test_greenhouse_connector_collects_jobs(organization: OrganizationConfig) -> None:
    session = FakeSession({"jobs": [{"id": 1, "title": "Senior SDET"}]})
    source = GreenhouseSource(Settings(collection_timeout_seconds=1), session=session)

    records = source.collect(organization)

    assert len(records) == 1
    assert records[0].source == "greenhouse"
    assert records[0].raw["title"] == "Senior SDET"
    assert "api.greenhouse.io" in session.last_url


def test_lever_connector_collects_postings() -> None:
    organization = OrganizationConfig(name="LeverCo", source="lever", identifier="leverco")
    session = FakeSession([{"id": "abc", "text": "Staff Quality Engineer"}])
    source = LeverSource(Settings(collection_timeout_seconds=1), session=session)

    records = source.collect(organization)

    assert len(records) == 1
    assert records[0].source == "lever"
    assert records[0].organization.identifier == "leverco"


def test_ashby_connector_collects_jobs() -> None:
    organization = OrganizationConfig(name="AshbyCo", source="ashby", identifier="ashbyco")
    session = FakeSession({"jobs": [{"id": "job_1", "title": "Quality Architect"}]})
    source = AshbySource(Settings(collection_timeout_seconds=1), session=session)

    records = source.collect(organization)

    assert len(records) == 1
    assert records[0].source == "ashby"
    assert records[0].raw["id"] == "job_1"


def test_source_factory_returns_registered_source() -> None:
    source = SourceFactory(Settings()).get("greenhouse")

    assert isinstance(source, GreenhouseSource)


def test_future_source_raises_for_unimplemented_source() -> None:
    organization = OrganizationConfig(name="FutureCo", source="workday", identifier="future")

    try:
        FutureSource(Settings()).collect(organization)
    except NotImplementedError as exc:
        assert "workday" in str(exc)
    else:
        raise AssertionError("Expected NotImplementedError")
