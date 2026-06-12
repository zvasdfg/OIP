from __future__ import annotations

from src.models.opportunity import SourceRecord
from src.models.organization import OrganizationConfig
from src.sources.base import OpportunitySource


class FutureSource(OpportunitySource):
    """Interface placeholder for sources that need source-specific discovery work."""

    source_name = "future"

    def collect(self, organization: OrganizationConfig) -> list[SourceRecord]:
        raise NotImplementedError(f"{organization.source.value} connector is not implemented yet")

