from __future__ import annotations

import logging

import requests

from src.config.settings import Settings
from src.sources.http import build_session

logger = logging.getLogger(__name__)


class TelegramNotifier:
    def __init__(self, settings: Settings, session: requests.Session | None = None) -> None:
        self.settings = settings
        self.session = session or build_session(settings)

    def enabled(self) -> bool:
        return bool(self.settings.telegram_bot_token and self.settings.telegram_chat_id)

    def send(self, body: str) -> bool:
        if not self.enabled():
            logger.info("Telegram notification skipped because bot settings are incomplete")
            return False
        url = f"https://api.telegram.org/bot{self.settings.telegram_bot_token}/sendMessage"
        response = self.session.post(
            url,
            json={"chat_id": self.settings.telegram_chat_id, "text": body, "disable_web_page_preview": True},
            timeout=20,
        )
        response.raise_for_status()
        return True

