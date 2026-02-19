from __future__ import annotations

from datetime import datetime
from typing import Optional, Sequence

from common.ingestion_types import IngestedInvoice, IngestionSource
from ports.outbound.intake_repository_port import IntakeRepositoryPort


class InMemoryIntakeRepositoryAdapter(IntakeRepositoryPort):
    def __init__(self) -> None:
        self._items: dict[str, IngestedInvoice] = {}

    def find_by_dedupe_key(self, dedupe_key: str) -> Optional[IngestedInvoice]:
        return self._items.get(dedupe_key)

    def save_new(self, invoice: IngestedInvoice) -> IngestedInvoice:
        self._items[invoice.dedupe_key] = invoice
        return invoice

    def append_history(self, dedupe_key: str, source: IngestionSource, processed_at: datetime, status: str) -> IngestedInvoice:
        invoice = self._items[dedupe_key]
        invoice.record_event(source=source, ingested_at=processed_at, status=status)
        return invoice

    def list_by_source_sorted(self, source: Optional[IngestionSource], newest_first: bool = True) -> Sequence[IngestedInvoice]:
        filtered = [
            invoice
            for invoice in self._items.values()
            if source is None or any(event.source == source for event in invoice.history)
        ]
        return sorted(
            filtered,
            key=lambda invoice: max(event.ingested_at for event in invoice.history),
            reverse=newest_first,
        )
