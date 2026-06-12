from __future__ import annotations

import logging

from src.config.settings import Settings
from src.models.evaluation import OpportunityScore
from src.models.opportunity import Opportunity
from src.notifications.email import EmailNotifier
from src.notifications.telegram import TelegramNotifier

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, settings: Settings) -> None:
        self.email = EmailNotifier(settings)
        self.telegram = TelegramNotifier(settings)

    def send_daily(self, ranked: list[tuple[Opportunity, OpportunityScore]]) -> dict[str, bool]:
        body = self.format_daily(ranked)
        subject = "Daily Opportunity Intelligence Report"
        results = {
            "email": self.email.send(subject, body),
            "telegram": self.telegram.send(body),
        }
        logger.info("Notification results", extra={"results": results})
        return results

    @staticmethod
    def format_daily(ranked: list[tuple[Opportunity, OpportunityScore]], limit: int = 10) -> str:
        lines = ["DAILY OPPORTUNITY INTELLIGENCE REPORT", ""]
        for index, (opportunity, score) in enumerate(ranked[:limit], start=1):
            lines.extend(
                [
                    f"{index}. {opportunity.organization}",
                    opportunity.title,
                    f"Alignment Score: {score.alignment_score}",
                    "",
                ]
            )
        if len(lines) == 2:
            lines.append("No ranked opportunities are available yet.")
        return "\n".join(lines).strip()

