from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from src.models.organization import OrganizationConfig
from src.models.profile import ProfessionalProfile


class ConfigLoader:
    def __init__(self, organizations_path: Path, profile_path: Path) -> None:
        self.organizations_path = organizations_path
        self.profile_path = profile_path

    def load_organizations(self) -> list[OrganizationConfig]:
        payload = self._read_yaml(self.organizations_path)
        if not isinstance(payload, list):
            raise ValueError(f"{self.organizations_path} must contain a YAML list")
        return [OrganizationConfig.model_validate(item) for item in payload]

    def load_profile(self) -> ProfessionalProfile:
        payload = self._read_yaml(self.profile_path)
        if not isinstance(payload, dict):
            raise ValueError(f"{self.profile_path} must contain a YAML mapping")
        return ProfessionalProfile.model_validate(payload)

    @staticmethod
    def _read_yaml(path: Path) -> Any:
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")
        with path.open("r", encoding="utf-8") as file:
            return yaml.safe_load(file) or {}

