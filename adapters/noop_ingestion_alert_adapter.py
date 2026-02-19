from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from common.ingestion_types import IngestionSource
from ports.outbound.ingestion_alert_port import IngestionAlertPort


@dataclass(frozen=True)
class IngestionAlertEvent:
    source: IngestionSource
    error_type: str
    occurred_at: datetime


class NoopIngestionAlertAdapter(IngestionAlertPort):
    def __init__(self) -> None:
        self.events: list[IngestionAlertEvent] = []

    def notify_failure(self, source: IngestionSource, error_type: str, occurred_at: datetime) -> None:
        self.events.append(IngestionAlertEvent(source=source, error_type=error_type, occurred_at=occurred_at))
