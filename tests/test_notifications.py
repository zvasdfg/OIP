from __future__ import annotations

from src.config.settings import Settings
from src.notifications.email import EmailNotifier
from src.notifications.service import NotificationService
from src.notifications.telegram import TelegramNotifier


class FakeSMTP:
    sent = []
    logged_in = False

    def __init__(self, host: str, port: int, timeout: int):
        self.host = host
        self.port = port
        self.timeout = timeout

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def starttls(self) -> None:
        return None

    def login(self, username: str, password: str) -> None:
        self.__class__.logged_in = True

    def send_message(self, message) -> None:
        self.__class__.sent.append(message)


class FakeTelegramResponse:
    def raise_for_status(self) -> None:
        return None


class FakeTelegramSession:
    def __init__(self):
        self.payload = None

    def post(self, url: str, json: dict, timeout: int):
        self.payload = {"url": url, "json": json, "timeout": timeout}
        return FakeTelegramResponse()


def test_notification_format_daily(opportunity) -> None:
    from src.models.evaluation import OpportunityScore

    score = OpportunityScore(
        opportunity_id=opportunity.opportunity_id,
        alignment_score=94,
        tier="A",
        strategic_fit="high",
        engagement_priority="recommended",
        criterion_scores={},
        analysis="",
    )

    body = NotificationService.format_daily([(opportunity, score)])

    assert "DAILY OPPORTUNITY INTELLIGENCE REPORT" in body
    assert "ExampleCo" in body
    assert "Alignment Score: 94" in body


def test_email_notifier_sends_when_configured(monkeypatch) -> None:
    FakeSMTP.sent = []
    monkeypatch.setattr("smtplib.SMTP", FakeSMTP)
    settings = Settings(
        smtp_host="smtp.example.com",
        smtp_from="from@example.com",
        smtp_to=["to@example.com"],
        smtp_username="user",
        smtp_password="secret",
    )

    sent = EmailNotifier(settings).send("Subject", "Body")

    assert sent is True
    assert FakeSMTP.sent[0]["Subject"] == "Subject"
    assert FakeSMTP.logged_in is True


def test_email_notifier_skips_when_disabled() -> None:
    assert EmailNotifier(Settings()).send("Subject", "Body") is False


def test_telegram_notifier_sends_when_configured() -> None:
    session = FakeTelegramSession()
    settings = Settings(telegram_bot_token="token", telegram_chat_id="chat")

    sent = TelegramNotifier(settings, session=session).send("Hello")

    assert sent is True
    assert session.payload["json"]["text"] == "Hello"


def test_telegram_notifier_skips_when_disabled() -> None:
    assert TelegramNotifier(Settings(), session=FakeTelegramSession()).send("Hello") is False

