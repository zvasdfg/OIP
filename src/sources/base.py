from __future__ import annotations

from abc import ABC, abstractmethod

import requests

from src.config.settings import Settings
from src.models.opportunity import SourceRecord
from src.models.organization import OrganizationConfig


class OpportunitySource(ABC):
    source_name: str

    def __init__(self, settings: Settings, session: requests.Session | None = None) -> None:
        self.settings = settings
        self.session = session

    @abstractmethod
    def collect(self, organization: OrganizationConfig) -> list[SourceRecord]:
        """Collect source-specific opportunity records for one organization."""

