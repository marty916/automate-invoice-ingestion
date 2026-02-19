from __future__ import annotations

from datetime import datetime
from typing import Optional, Sequence

from common.ingestion_types import IngestedInvoice, IngestionSource, InvoiceMetadata
from domain.invoice_dedupe_policy import InvoiceDedupePolicy
from ports.inbound.invoice_ingestion_port import InvoiceIngestionPort
from ports.outbound.accounting_source_port import AccountingSourcePort
from ports.outbound.ap_email_source_port import ApEmailSourcePort
from ports.outbound.ingestion_alert_port import IngestionAlertPort, IngestionFailureEvent
from ports.outbound.intake_repository_port import IntakeRepositoryPort


class InvoiceIngestionService(InvoiceIngestionPort):
    def __init__(
        self,
        intake_repository: IntakeRepositoryPort,
        alert_port: IngestionAlertPort,
        ap_email_source: Optional[ApEmailSourcePort] = None,
        accounting_source: Optional[AccountingSourcePort] = None,
        dedupe_policy: type[InvoiceDedupePolicy] = InvoiceDedupePolicy,
    ) -> None:
        self._intake_repository = intake_repository
        self._alert_port = alert_port
        self._ap_email_source = ap_email_source
        self._accounting_source = accounting_source
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

    def process_ap_email_inbox(self, processed_at: datetime) -> Sequence[IngestedInvoice]:
        source = self._require_ap_email_source()
        try:
            payloads = source.fetch_new_invoices()
        except RuntimeError:
            self.record_ingestion_failure(
                source=IngestionSource.AP_EMAIL,
                error_type="fetch_failed",
                occurred_at=processed_at,
            )
            return []

        ingested: list[IngestedInvoice] = []
        for payload in payloads:
            ingested.append(
                self.ingest_ap_email_invoice(
                    source_id=payload.source_id,
                    metadata=payload.metadata,
                    file_hash=payload.file_hash,
                    processed_at=processed_at,
                )
            )
        return ingested

    def process_accounting_sync(self, processed_at: datetime) -> Sequence[IngestedInvoice]:
        source = self._require_accounting_source()
        try:
            payloads = source.fetch_new_invoices()
        except RuntimeError:
            self.record_ingestion_failure(
                source=IngestionSource.ACCOUNTING_SYSTEM,
                error_type="fetch_failed",
                occurred_at=processed_at,
            )
            return []

        ingested: list[IngestedInvoice] = []
        for payload in payloads:
            ingested.append(
                self.ingest_accounting_invoice(
                    source_id=payload.source_id,
                    metadata=payload.metadata,
                    file_hash=payload.file_hash,
                    processed_at=processed_at,
                )
            )
        return ingested

    def record_ingestion_failure(self, source: IngestionSource, error_type: str, occurred_at: datetime) -> None:
        self._alert_port.notify_failure(
            source=source, error_type=error_type, occurred_at=occurred_at)

    def list_ingestion_failures(self) -> Sequence[IngestionFailureEvent]:
        return self._alert_port.list_failures()

    def _require_ap_email_source(self) -> ApEmailSourcePort:
        if self._ap_email_source is None:
            raise RuntimeError("AP email source port is not configured")
        return self._ap_email_source

    def _require_accounting_source(self) -> AccountingSourcePort:
        if self._accounting_source is None:
            raise RuntimeError("Accounting source port is not configured")
        return self._accounting_source

    def _ingest_one(
        self,
        source: IngestionSource,
        source_id: str,
        metadata: InvoiceMetadata,
        file_hash: Optional[str],
        processed_at: datetime,
    ) -> IngestedInvoice:
        dedupe_key = self._dedupe_policy.build_dedupe_key(
            metadata=metadata, file_hash=file_hash)
        existing = self._intake_repository.find_by_dedupe_key(dedupe_key)
        if existing:
            return self._intake_repository.append_history(
                dedupe_key=dedupe_key,
                source=source,
                processed_at=processed_at,
                status=f"duplicate_seen:{source_id}",
            )

        invoice = IngestedInvoice(
            dedupe_key=dedupe_key, metadata=metadata, file_hash=file_hash)
        invoice.record_event(
            source=source, ingested_at=processed_at, status=f"ingested:{source_id}")
        return self._intake_repository.save_new(invoice)
