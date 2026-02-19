from __future__ import annotations

from datetime import datetime
from typing import Optional, Sequence

from common.ingestion_types import IngestedInvoice, IngestionSource, InvoiceMetadata
from domain.invoice_dedupe_policy import InvoiceDedupePolicy
from ports.inbound.invoice_ingestion_port import InvoiceIngestionPort
from ports.outbound.ingestion_alert_port import IngestionAlertPort
from ports.outbound.intake_repository_port import IntakeRepositoryPort


class InvoiceIngestionService(InvoiceIngestionPort):
    def __init__(
        self,
        intake_repository: IntakeRepositoryPort,
        alert_port: IngestionAlertPort,
        dedupe_policy: type[InvoiceDedupePolicy] = InvoiceDedupePolicy,
    ) -> None:
        self._intake_repository = intake_repository
        self._alert_port = alert_port
        self._dedupe_policy = dedupe_policy

    def ingest_ap_email_invoice(
        self,
        source_id: str,
        metadata: InvoiceMetadata,
        file_hash: Optional[str],
        processed_at: datetime,
    ) -> IngestedInvoice:
        return self._ingest_one(
            source=IngestionSource.AP_EMAIL,
            source_id=source_id,
            metadata=metadata,
            file_hash=file_hash,
            processed_at=processed_at,
        )

    def ingest_accounting_invoice(
        self,
        source_id: str,
        metadata: InvoiceMetadata,
        file_hash: Optional[str],
        processed_at: datetime,
    ) -> IngestedInvoice:
        return self._ingest_one(
            source=IngestionSource.ACCOUNTING_SYSTEM,
            source_id=source_id,
            metadata=metadata,
            file_hash=file_hash,
            processed_at=processed_at,
        )

    def list_for_analyst(
        self,
        source: Optional[IngestionSource],
        newest_first: bool = True,
    ) -> Sequence[IngestedInvoice]:
        return self._intake_repository.list_by_source_sorted(source=source, newest_first=newest_first)

    def record_ingestion_failure(self, source: IngestionSource, error_type: str, occurred_at: datetime) -> None:
        self._alert_port.notify_failure(source=source, error_type=error_type, occurred_at=occurred_at)

    def _ingest_one(
        self,
        source: IngestionSource,
        source_id: str,
        metadata: InvoiceMetadata,
        file_hash: Optional[str],
        processed_at: datetime,
    ) -> IngestedInvoice:
        dedupe_key = self._dedupe_policy.build_dedupe_key(metadata=metadata, file_hash=file_hash)
        existing = self._intake_repository.find_by_dedupe_key(dedupe_key)
        if existing:
            return self._intake_repository.append_history(
                dedupe_key=dedupe_key,
                source=source,
                processed_at=processed_at,
                status=f"duplicate_seen:{source_id}",
            )

        invoice = IngestedInvoice(dedupe_key=dedupe_key, metadata=metadata, file_hash=file_hash)
        invoice.record_event(source=source, ingested_at=processed_at, status=f"ingested:{source_id}")
        return self._intake_repository.save_new(invoice)
