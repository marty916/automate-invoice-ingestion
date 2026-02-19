from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Sequence

from common.ingestion_types import IngestedInvoice, IngestionSource, InvoiceMetadata


class InvoiceIngestionPort(ABC):
    @abstractmethod
    def ingest_ap_email_invoice(
        self,
        source_id: str,
        metadata: InvoiceMetadata,
        file_hash: Optional[str],
        processed_at: datetime,
    ) -> IngestedInvoice:
        raise NotImplementedError

    @abstractmethod
    def ingest_accounting_invoice(
        self,
        source_id: str,
        metadata: InvoiceMetadata,
        file_hash: Optional[str],
        processed_at: datetime,
    ) -> IngestedInvoice:
        raise NotImplementedError

    @abstractmethod
    def list_for_analyst(
        self,
        source: Optional[IngestionSource],
        newest_first: bool = True,
    ) -> Sequence[IngestedInvoice]:
        raise NotImplementedError

    @abstractmethod
    def process_ap_email_inbox(self, processed_at: datetime) -> Sequence[IngestedInvoice]:
        raise NotImplementedError

    @abstractmethod
    def process_accounting_sync(self, processed_at: datetime) -> Sequence[IngestedInvoice]:
        raise NotImplementedError
