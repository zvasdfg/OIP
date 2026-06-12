from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from src.config.settings import Settings

logger = logging.getLogger(__name__)


class EmailNotifier:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def enabled(self) -> bool:
        return bool(self.settings.smtp_host and self.settings.smtp_from and self.settings.smtp_to)

    def send(self, subject: str, body: str) -> bool:
        if not self.enabled():
            logger.info("SMTP notification skipped because email settings are incomplete")
            return False

        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = self.settings.smtp_from or ""
        message["To"] = ", ".join(self.settings.smtp_to)
        message.set_content(body)

        with smtplib.SMTP(self.settings.smtp_host or "", self.settings.smtp_port, timeout=20) as smtp:
            smtp.starttls()
            if self.settings.smtp_username and self.settings.smtp_password:
                smtp.login(self.settings.smtp_username, self.settings.smtp_password)
            smtp.send_message(message)
        return True

