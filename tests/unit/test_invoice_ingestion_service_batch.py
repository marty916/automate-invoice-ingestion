from __future__ import annotations

from datetime import datetime

from adapters.in_memory_intake_repository_adapter import InMemoryIntakeRepositoryAdapter
from adapters.noop_ingestion_alert_adapter import NoopIngestionAlertAdapter
from common.ingestion_types import IngestionSource, InvoiceMetadata, SourceInvoicePayload
from ports.outbound.accounting_source_port import AccountingSourcePort
from ports.outbound.ap_email_source_port import ApEmailSourcePort
from services.invoice_ingestion_service import InvoiceIngestionService


class FakeApEmailSource(ApEmailSourcePort):
    def __init__(self, payloads: list[SourceInvoicePayload]) -> None:
        self._payloads = payloads

    def fetch_new_invoices(self) -> list[SourceInvoicePayload]:
        return list(self._payloads)


class FakeAccountingSource(AccountingSourcePort):
    def __init__(self, payloads: list[SourceInvoicePayload]) -> None:
        self._payloads = payloads

    def fetch_new_invoices(self) -> list[SourceInvoicePayload]:
        return list(self._payloads)


class FailingApEmailSource(ApEmailSourcePort):
    def fetch_new_invoices(self) -> list[SourceInvoicePayload]:
        raise RuntimeError("upstream unavailable")


class FailingAccountingSource(AccountingSourcePort):
    def fetch_new_invoices(self) -> list[SourceInvoicePayload]:
        raise RuntimeError("upstream unavailable")


def _metadata(invoice_number: str) -> InvoiceMetadata:
    return InvoiceMetadata(
        invoice_number=invoice_number,
        supplier="Fabrikam",
        amount=100.0,
        invoice_date=datetime(2026, 2, 10),
    )


def test_batch_processing_ap_email_and_accounting_dedupes_cross_source() -> None:
    repository = InMemoryIntakeRepositoryAdapter()
    alerts = NoopIngestionAlertAdapter()
    processed_at = datetime(2026, 2, 19, 10, 0, 0)

    ap_source = FakeApEmailSource(
        [
            SourceInvoicePayload(
                source_id="mail-1",
                metadata=_metadata("INV-400"),
                file_hash="hash-email",
                received_at=processed_at,
            )
        ]
    )
    accounting_source = FakeAccountingSource(
        [
            SourceInvoicePayload(
                source_id="acct-1",
                metadata=_metadata("INV-400"),
                file_hash="hash-acct",
                received_at=processed_at,
            )
        ]
    )

    service = InvoiceIngestionService(
        intake_repository=repository,
        alert_port=alerts,
        ap_email_source=ap_source,
        accounting_source=accounting_source,
    )

    ap_results = service.process_ap_email_inbox(processed_at=processed_at)
    acct_results = service.process_accounting_sync(processed_at=processed_at)

    assert len(ap_results) == 1
    assert len(acct_results) == 1
    all_items = list(repository.list_by_source_sorted(source=None))
    assert len(all_items) == 1
    history_sources = {event.source for event in all_items[0].history}
    assert history_sources == {
        IngestionSource.AP_EMAIL, IngestionSource.ACCOUNTING_SYSTEM}


def test_batch_processing_records_alert_when_ap_source_fails() -> None:
    repository = InMemoryIntakeRepositoryAdapter()
    alerts = NoopIngestionAlertAdapter()
    accounting_source = FakeAccountingSource([])

    service = InvoiceIngestionService(
        intake_repository=repository,
        alert_port=alerts,
        ap_email_source=FailingApEmailSource(),
        accounting_source=accounting_source,
    )

    results = service.process_ap_email_inbox(
        processed_at=datetime(2026, 2, 19, 11, 0, 0))

    assert results == []
    assert len(alerts.events) == 1
    assert alerts.events[0].source == IngestionSource.AP_EMAIL
    assert alerts.events[0].error_type == "fetch_failed"


def test_batch_processing_records_alert_when_accounting_source_fails() -> None:
    repository = InMemoryIntakeRepositoryAdapter()
    alerts = NoopIngestionAlertAdapter()
    ap_source = FakeApEmailSource([])

    service = InvoiceIngestionService(
        intake_repository=repository,
        alert_port=alerts,
        ap_email_source=ap_source,
        accounting_source=FailingAccountingSource(),
    )

    results = service.process_accounting_sync(
        processed_at=datetime(2026, 2, 19, 11, 0, 0))

    assert results == []
    assert len(alerts.events) == 1
    assert alerts.events[0].source == IngestionSource.ACCOUNTING_SYSTEM
    assert alerts.events[0].error_type == "fetch_failed"
