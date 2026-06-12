from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from typing import Any

from bs4 import BeautifulSoup

from src.models.opportunity import Opportunity, SourceRecord

REMOTE_PATTERN = re.compile(r"\b(remote|distributed|work from home|anywhere|global)\b", re.IGNORECASE)


class OpportunityNormalizer:
    def normalize_many(self, records: list[SourceRecord]) -> list[Opportunity]:
        normalized: list[Opportunity] = []
        for record in records:
            opportunity = self.normalize(record)
            if opportunity is not None:
                normalized.append(opportunity)
        return normalized

    def normalize(self, record: SourceRecord) -> Opportunity | None:
        if record.source == "greenhouse":
            return self._normalize_greenhouse(record)
        if record.source == "lever":
            return self._normalize_lever(record)
        if record.source == "ashby":
            return self._normalize_ashby(record)
        return None

    def _normalize_greenhouse(self, record: SourceRecord) -> Opportunity | None:
        raw = record.raw
        title = _as_text(raw.get("title"))
        if not title:
            return None
        location = _extract_greenhouse_location(raw)
        description = _clean_html(_as_text(raw.get("content")))
        department = _first_department(raw.get("departments"))
        url = raw.get("absolute_url")
        external_id = _as_text(raw.get("id")) or _stable_hash(raw)
        date_published = _parse_datetime(raw.get("first_published") or raw.get("updated_at"))
        metadata = {
            "identifier": record.organization.identifier,
            "priority": record.organization.priority,
            "category": record.organization.category,
            "region": record.organization.region,
            "tags": record.organization.tags,
            "raw_id": external_id,
            "offices": raw.get("offices", []),
        }
        return Opportunity(
            opportunity_id=_opportunity_id(record.source, record.organization.identifier, external_id, title, url),
            organization=record.organization.name,
            title=title,
            location=location,
            remote=_is_remote(title, location, description),
            description=description,
            department=department,
            url=url,
            compensation=_extract_compensation(raw),
            date_published=date_published,
            source=record.source,
            metadata=metadata,
        )

    def _normalize_lever(self, record: SourceRecord) -> Opportunity | None:
        raw = record.raw
        title = _as_text(raw.get("text"))
        if not title:
            return None
        categories = raw.get("categories") or {}
        location = _as_text(categories.get("location"))
        department = _as_text(categories.get("department") or categories.get("team"))
        description = _clean_html(
            _as_text(raw.get("descriptionPlain") or raw.get("description") or raw.get("additionalPlain") or "")
        )
        external_id = _as_text(raw.get("id")) or _stable_hash(raw)
        date_published = _parse_datetime(raw.get("createdAt") or raw.get("updatedAt"))
        metadata = {
            "identifier": record.organization.identifier,
            "priority": record.organization.priority,
            "category": record.organization.category,
            "region": record.organization.region,
            "tags": record.organization.tags,
            "raw_id": external_id,
            "commitment": categories.get("commitment"),
            "lists": raw.get("lists", []),
        }
        url = raw.get("hostedUrl") or raw.get("applyUrl")
        return Opportunity(
            opportunity_id=_opportunity_id(record.source, record.organization.identifier, external_id, title, url),
            organization=record.organization.name,
            title=title,
            location=location,
            remote=_is_remote(title, location, description),
            description=description,
            department=department,
            url=url,
            compensation=_extract_compensation(raw),
            date_published=date_published,
            source=record.source,
            metadata=metadata,
        )

    def _normalize_ashby(self, record: SourceRecord) -> Opportunity | None:
        raw = record.raw
        title = _as_text(raw.get("title"))
        if not title:
            return None
        location_payload = raw.get("location")
        location = _as_text(location_payload.get("name")) if isinstance(location_payload, dict) else _as_text(location_payload)
        department_payload = raw.get("department")
        department = (
            _as_text(department_payload.get("name")) if isinstance(department_payload, dict) else _as_text(department_payload)
        )
        description = _clean_html(_as_text(raw.get("descriptionPlain") or raw.get("descriptionHtml") or raw.get("description")))
        external_id = _as_text(raw.get("id")) or _stable_hash(raw)
        url = raw.get("jobUrl") or raw.get("externalLink")
        metadata = {
            "identifier": record.organization.identifier,
            "priority": record.organization.priority,
            "category": record.organization.category,
            "region": record.organization.region,
            "tags": record.organization.tags,
            "raw_id": external_id,
            "employment_type": raw.get("employmentType"),
        }
        return Opportunity(
            opportunity_id=_opportunity_id(record.source, record.organization.identifier, external_id, title, url),
            organization=record.organization.name,
            title=title,
            location=location,
            remote=_is_remote(title, location, description),
            description=description,
            department=department,
            url=url,
            compensation=_extract_compensation(raw),
            date_published=_parse_datetime(raw.get("publishedDate") or raw.get("updatedAt")),
            source=record.source,
            metadata=metadata,
        )


def _clean_html(value: str) -> str:
    if not value:
        return ""
    text = BeautifulSoup(value, "html.parser").get_text(" ")
    return re.sub(r"\s+", " ", text).strip()


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _extract_greenhouse_location(raw: dict[str, Any]) -> str | None:
    location = raw.get("location")
    if isinstance(location, dict):
        return _as_text(location.get("name")) or None
    return _as_text(location) or None


def _first_department(departments: Any) -> str | None:
    if isinstance(departments, list) and departments:
        first = departments[0]
        if isinstance(first, dict):
            return _as_text(first.get("name")) or None
        return _as_text(first) or None
    return None


def _is_remote(title: str, location: str | None, description: str) -> bool:
    return bool(REMOTE_PATTERN.search(" ".join([title, location or "", description])))


def _parse_datetime(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, (int, float)):
        timestamp = value / 1000 if value > 10_000_000_000 else value
        return datetime.fromtimestamp(timestamp, tz=UTC)
    text = str(value).strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def _extract_compensation(raw: dict[str, Any]) -> str | None:
    for key in ("compensation", "salary", "salaryRange", "payRange"):
        value = raw.get(key)
        if value:
            return _as_text(value)
    ranges = raw.get("pay_input_ranges")
    if isinstance(ranges, list) and ranges:
        return json.dumps(ranges, sort_keys=True)
    return None


def _opportunity_id(source: str, identifier: str, external_id: str, title: str, url: Any) -> str:
    return hashlib.sha256(f"{source}:{identifier}:{external_id}:{title}:{url or ''}".encode("utf-8")).hexdigest()


def _stable_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode("utf-8")).hexdigest()

