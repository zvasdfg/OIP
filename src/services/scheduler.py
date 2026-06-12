from __future__ import annotations

import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from src.config.settings import Settings
from src.services.pipeline import OpportunityPipeline

logger = logging.getLogger(__name__)


class SchedulerService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.scheduler = BlockingScheduler(timezone=settings.timezone)

    def start(self) -> None:
        trigger = CronTrigger(hour=8, minute=0, timezone=self.settings.timezone)
        self.scheduler.add_job(self._run_pipeline, trigger, id="daily_opportunity_intelligence", replace_existing=True)
        logger.info("Scheduler started", extra={"timezone": self.settings.timezone, "schedule": "08:00"})
        self.scheduler.start()

    def _run_pipeline(self) -> None:
        OpportunityPipeline(self.settings).run_once()

