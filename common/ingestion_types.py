from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class IngestionSource(str, Enum):
    AP_EMAIL = "AP email"
    ACCOUNTING_SYSTEM = "Accounting system"


@dataclass(frozen=True)
class InvoiceMetadata:
    invoice_number: str
    supplier: str
    amount: float
    invoice_date: datetime


@dataclass(frozen=True)
class SourceInvoicePayload:
    source_id: str
    metadata: InvoiceMetadata
    file_hash: Optional[str]
    received_at: datetime


@dataclass
class IngestionHistoryEntry:
    source: IngestionSource
    ingested_at: datetime
    status: str


@dataclass
class IngestedInvoice:
    dedupe_key: str
    metadata: InvoiceMetadata
    file_hash: Optional[str]
    history: list[IngestionHistoryEntry] = field(default_factory=list)

    def record_event(self, source: IngestionSource, ingested_at: datetime, status: str) -> None:
        self.history.append(IngestionHistoryEntry(source=source, ingested_at=ingested_at, status=status))
