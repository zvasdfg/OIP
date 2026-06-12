from __future__ import annotations

from collections.abc import Callable

import requests

from src.config.settings import Settings
from src.models.organization import SourceType
from src.sources.ashby import AshbySource
from src.sources.base import OpportunitySource
from src.sources.future import FutureSource
from src.sources.greenhouse import GreenhouseSource
from src.sources.lever import LeverSource


class SourceFactory:
    def __init__(self, settings: Settings, session: requests.Session | None = None) -> None:
        self.settings = settings
        self.session = session
        self._registry: dict[SourceType, Callable[[Settings, requests.Session | None], OpportunitySource]] = {
            SourceType.GREENHOUSE: GreenhouseSource,
            SourceType.LEVER: LeverSource,
            SourceType.ASHBY: AshbySource,
            SourceType.WORKDAY: FutureSource,
            SourceType.BAMBOOHR: FutureSource,
            SourceType.SMARTRECRUITERS: FutureSource,
            SourceType.RECRUITEE: FutureSource,
        }

    def get(self, source_type: SourceType) -> OpportunitySource:
        source_class = self._registry[source_type]
        return source_class(self.settings, self.session)

