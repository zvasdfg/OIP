# Opportunity Intelligence Platform

Opportunity Intelligence Platform (OIP) aggregates public professional opportunity feeds, normalizes source-specific records, evaluates alignment against a configurable professional profile, ranks opportunities, stores longitudinal snapshots, and generates daily intelligence reports.

## Architecture

The project follows a Clean Architecture style under `src/`:

- `sources`: public feed connectors for Greenhouse, Lever, and Ashby, plus future-source abstractions.
- `normalization`: source-specific mapping into the common `Opportunity` model.
- `evaluation`: weighted scoring engine for strategic fit, expertise fit, domain fit, work model, and leadership signals.
- `ranking`: Tier A/B/C/D categorization.
- `intelligence`: contextual insight generation.
- `storage`: SQLAlchemy repositories and SQLite schema designed for PostgreSQL migration.
- `reporting`: Jinja2 daily HTML intelligence report.
- `notifications`: SMTP email and Telegram notifications.
- `services`: orchestration pipeline and APScheduler integration.
- `dashboard`: Streamlit analytics dashboard.
- `cli`: Typer commands.

## Setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

The default database is `sqlite:///data/oip.sqlite3`. Runtime settings are controlled through `OIP_*` environment variables.

## Configuration

Organizations live in `config/organizations.yaml`. Each entry supports:

```yaml
- name: Datadog
  source: greenhouse
  identifier: datadog
  priority: high
  category: observability
  region: global
  tags: [cloud, infrastructure, developer tools]
```

The registry can scale to hundreds or thousands of organizations because collection is source-abstracted and persistence is incremental by deterministic opportunity ID.

The professional profile lives in `config/professional_profile.yaml` and defines expertise, preferred domains, target titles, excluded titles, and work-model preferences.

## CLI

```bash
python main.py collect
python main.py evaluate
python main.py rank
python main.py report
python main.py notify
python main.py run
python main.py schedule
```

`run` executes the full daily workflow: collect, normalize, evaluate, rank, report, and notify.

## Scheduling

The scheduler runs daily at `08:00` in `America/Mexico_City` by default.

```bash
python main.py schedule
```

Override timezone with:

```bash
export OIP_TIMEZONE=America/Mexico_City
```

## Reports

Daily reports are generated at:

```text
reports/daily_intelligence_report.html
```

Sections include executive summary, priority opportunities, market signals, gap analysis, and strategic recommendations.

## Notifications

SMTP and Telegram are optional. Set the relevant values in `.env`:

```bash
OIP_SMTP_HOST=smtp.example.com
OIP_SMTP_FROM=oip@example.com
OIP_SMTP_TO=recipient@example.com
OIP_TELEGRAM_BOT_TOKEN=...
OIP_TELEGRAM_CHAT_ID=...
```

If credentials are missing, notification channels are skipped without failing the pipeline.

## Dashboard

```bash
streamlit run src/dashboard/app.py
```

The dashboard includes opportunity feed, intelligence rankings, market signals, engagement pipeline, and metrics tabs.

## Adding New Sources

1. Implement `OpportunitySource.collect()` in `src/sources/`.
2. Register the source in `SourceFactory`.
3. Add source-specific mapping in `OpportunityNormalizer`.
4. Add connector and normalization tests.

Future abstractions already exist for Workday, BambooHR, SmartRecruiters, and Recruitee.

## Extending Evaluation Models

The weighted scoring model is in `src/evaluation/engine.py`. Add criteria by:

1. Adding a named weight.
2. Producing a normalized `0.0` to `1.0` criterion score.
3. Including the criterion in `EvaluationResult.criterion_scores`.
4. Updating tests to capture expected behavior.

## Docker

```bash
docker compose up --build oip
docker compose up --build dashboard
```

The compose file mounts `config`, `data`, and `reports` so state survives container restarts.

## Testing

```bash
pytest
```

The test suite covers source connectors, normalization, evaluation, ranking, intelligence, reporting, and storage behavior.

