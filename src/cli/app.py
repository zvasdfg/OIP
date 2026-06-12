from __future__ import annotations

import json
import logging

import typer

from src.config.logging import configure_logging
from src.config.settings import get_settings
from src.services.pipeline import OpportunityPipeline
from src.services.scheduler import SchedulerService

app = typer.Typer(help="Opportunity Intelligence Platform")


def _pipeline() -> OpportunityPipeline:
    configure_logging(logging.INFO)
    return OpportunityPipeline(get_settings())


@app.command()
def collect() -> None:
    """Collect and normalize opportunities from configured public sources."""
    result = _pipeline().collect()
    typer.echo(json.dumps(result, indent=2))


@app.command()
def evaluate(limit: int | None = typer.Option(None, help="Optional maximum number of opportunities to evaluate.")) -> None:
    """Evaluate stored opportunities against the professional profile."""
    result = _pipeline().evaluate(limit=limit)
    typer.echo(json.dumps(result, indent=2))


@app.command()
def rank(limit: int = typer.Option(25, help="Number of ranked opportunities to display.")) -> None:
    """Show the top ranked opportunities."""
    ranked = _pipeline().rank(limit=limit)
    for index, (opportunity, score) in enumerate(ranked, start=1):
        typer.echo(f"{index}. {opportunity.organization} | {opportunity.title} | {score.alignment_score} | Tier {score.tier}")


@app.command()
def report(limit: int = typer.Option(50, help="Number of ranked opportunities to include.")) -> None:
    """Generate the HTML daily intelligence report."""
    path = _pipeline().report(limit=limit)
    typer.echo(str(path))


@app.command()
def notify(limit: int = typer.Option(10, help="Number of opportunities to include.")) -> None:
    """Send configured email and Telegram notifications."""
    result = _pipeline().notify(limit=limit)
    typer.echo(json.dumps(result, indent=2))


@app.command("run")
def run_once() -> None:
    """Run collect, evaluate, rank, report, and notify once."""
    result = _pipeline().run_once()
    typer.echo(json.dumps(result, indent=2))


@app.command()
def schedule() -> None:
    """Start the daily scheduler at 08:00 in the configured timezone."""
    configure_logging(logging.INFO)
    SchedulerService(get_settings()).start()

