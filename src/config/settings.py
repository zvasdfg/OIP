from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field


class Settings(BaseModel):
    project_root: Path = Field(default_factory=lambda: Path.cwd())
    organizations_path: Path = Path("config/organizations.yaml")
    profile_path: Path = Path("config/professional_profile.yaml")
    database_url: str = "sqlite:///data/oip.sqlite3"
    reports_dir: Path = Path("reports")
    timezone: str = "America/Mexico_City"
    collection_timeout_seconds: int = 20
    max_retries: int = 3
    retry_backoff_factor: float = 0.6
    user_agent: str = "OIP/1.0 Opportunity Intelligence Platform"
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from: str | None = None
    smtp_to: list[str] = Field(default_factory=list)
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None

    @classmethod
    def from_environment(cls) -> "Settings":
        recipients = os.getenv("OIP_SMTP_TO", "")
        return cls(
            organizations_path=Path(os.getenv("OIP_ORGANIZATIONS_PATH", "config/organizations.yaml")),
            profile_path=Path(os.getenv("OIP_PROFILE_PATH", "config/professional_profile.yaml")),
            database_url=os.getenv("OIP_DATABASE_URL", "sqlite:///data/oip.sqlite3"),
            reports_dir=Path(os.getenv("OIP_REPORTS_DIR", "reports")),
            timezone=os.getenv("OIP_TIMEZONE", "America/Mexico_City"),
            collection_timeout_seconds=int(os.getenv("OIP_COLLECTION_TIMEOUT_SECONDS", "20")),
            max_retries=int(os.getenv("OIP_MAX_RETRIES", "3")),
            retry_backoff_factor=float(os.getenv("OIP_RETRY_BACKOFF_FACTOR", "0.6")),
            user_agent=os.getenv("OIP_USER_AGENT", "OIP/1.0 Opportunity Intelligence Platform"),
            smtp_host=os.getenv("OIP_SMTP_HOST"),
            smtp_port=int(os.getenv("OIP_SMTP_PORT", "587")),
            smtp_username=os.getenv("OIP_SMTP_USERNAME"),
            smtp_password=os.getenv("OIP_SMTP_PASSWORD"),
            smtp_from=os.getenv("OIP_SMTP_FROM"),
            smtp_to=[item.strip() for item in recipients.split(",") if item.strip()],
            telegram_bot_token=os.getenv("OIP_TELEGRAM_BOT_TOKEN"),
            telegram_chat_id=os.getenv("OIP_TELEGRAM_CHAT_ID"),
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.from_environment()

