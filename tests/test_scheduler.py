from __future__ import annotations

from src.config.settings import Settings
from src.services.scheduler import SchedulerService


class FakeScheduler:
    def __init__(self, timezone: str):
        self.timezone = timezone
        self.jobs = []
        self.started = False

    def add_job(self, func, trigger, id: str, replace_existing: bool):
        self.jobs.append({"func": func, "trigger": trigger, "id": id, "replace_existing": replace_existing})

    def start(self) -> None:
        self.started = True


def test_scheduler_registers_daily_job(monkeypatch) -> None:
    holder = {}

    def factory(timezone: str):
        scheduler = FakeScheduler(timezone)
        holder["scheduler"] = scheduler
        return scheduler

    monkeypatch.setattr("src.services.scheduler.BlockingScheduler", factory)

    service = SchedulerService(Settings(timezone="America/Mexico_City"))
    service.start()

    scheduler = holder["scheduler"]
    assert scheduler.started is True
    assert scheduler.jobs[0]["id"] == "daily_opportunity_intelligence"

