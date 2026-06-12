from __future__ import annotations

import logging

import requests

from src.config.settings import Settings
from src.models.opportunity import SourceRecord
from src.models.organization import OrganizationConfig
from src.sources.base import OpportunitySource
from src.sources.http import build_session, get_json

logger = logging.getLogger(__name__)


class LeverSource(OpportunitySource):
    source_name = "lever"

    def __init__(self, settings: Settings, session: requests.Session | None = None) -> None:
        super().__init__(settings, session or build_session(settings))

    def collect(self, organization: OrganizationConfig) -> list[SourceRecord]:
        url = f"https://api.lever.co/v0/postings/{organization.identifier}?mode=json"
        try:
            payload = get_json(self.session, url, self.settings.collection_timeout_seconds)
        except requests.RequestException as exc:
            logger.warning(
                "Lever collection failed",
                extra={"organization": organization.name, "identifier": organization.identifier, "error": str(exc)},
            )
            return []
        postings = payload if isinstance(payload, list) else payload.get("postings", [])
        if not isinstance(postings, list):
            return []
        return [SourceRecord(source=self.source_name, organization=organization, raw=posting) for posting in postings]

