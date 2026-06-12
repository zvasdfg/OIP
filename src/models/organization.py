from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class SourceType(StrEnum):
    GREENHOUSE = "greenhouse"
    LEVER = "lever"
    ASHBY = "ashby"
    WORKDAY = "workday"
    BAMBOOHR = "bamboohr"
    SMARTRECRUITERS = "smartrecruiters"
    RECRUITEE = "recruitee"


class OrganizationConfig(BaseModel):
    name: str
    source: SourceType
    identifier: str
    priority: str = "medium"
    category: str | None = None
    region: str | None = None
    tags: list[str] = Field(default_factory=list)

    @field_validator("priority")
    @classmethod
    def normalize_priority(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in {"low", "medium", "high"}:
            return "medium"
        return normalized

