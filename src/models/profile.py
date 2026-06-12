from __future__ import annotations

from pydantic import BaseModel, Field


class ProfessionalProfile(BaseModel):
    expertise: list[str] = Field(default_factory=list)
    preferred_domains: list[str] = Field(default_factory=list)
    target_titles: list[str] = Field(default_factory=list)
    excluded_titles: list[str] = Field(default_factory=list)
    preferred_work_models: list[str] = Field(default_factory=lambda: ["remote", "distributed", "hybrid"])

    def normalized_expertise(self) -> set[str]:
        return {item.strip().lower() for item in self.expertise if item.strip()}

    def normalized_domains(self) -> set[str]:
        return {item.strip().lower() for item in self.preferred_domains if item.strip()}

