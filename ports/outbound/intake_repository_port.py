from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Sequence

from common.ingestion_types import IngestedInvoice, IngestionSource


class IntakeRepositoryPort(ABC):
    @abstractmethod
    def find_by_dedupe_key(self, dedupe_key: str) -> Optional[IngestedInvoice]:
        raise NotImplementedError

    @abstractmethod
    def save_new(self, invoice: IngestedInvoice) -> IngestedInvoice:
        raise NotImplementedError

    @abstractmethod
    def append_history(self, dedupe_key: str, source: IngestionSource, processed_at: datetime, status: str) -> IngestedInvoice:
        raise NotImplementedError

    @abstractmethod
    def list_by_source_sorted(self, source: Optional[IngestionSource], newest_first: bool = True) -> Sequence[IngestedInvoice]:
        raise NotImplementedError
