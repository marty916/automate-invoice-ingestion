from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Sequence

from common.ingestion_types import IngestionSource
from ports.outbound.ingestion_alert_port import IngestionAlertPort, IngestionFailureEvent


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

    def list_failures(self) -> Sequence[IngestionFailureEvent]:
        return [
            IngestionFailureEvent(source=event.source, error_type=event.error_type, occurred_at=event.occurred_at)
            for event in self.events
        ]
