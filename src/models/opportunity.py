from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field, HttpUrl

from src.models.organization import OrganizationConfig


class SourceRecord(BaseModel):
    source: str
    organization: OrganizationConfig
    raw: dict[str, Any]
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Opportunity(BaseModel):
    opportunity_id: str
    organization: str
    title: str
    location: str | None = None
    remote: bool = False
    description: str = ""
    department: str | None = None
    url: HttpUrl | str | None = None
    compensation: str | None = None
    date_published: datetime | None = None
    source: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    first_seen_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_seen_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @property
    def searchable_text(self) -> str:
        values = [
            self.organization,
            self.title,
            self.location or "",
            self.description,
            self.department or "",
            " ".join(str(value) for value in self.metadata.values()),
        ]
        return " ".join(values).lower()

