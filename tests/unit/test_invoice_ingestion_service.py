from __future__ import annotations

from datetime import datetime

from adapters.in_memory_intake_repository_adapter import InMemoryIntakeRepositoryAdapter
from adapters.noop_ingestion_alert_adapter import NoopIngestionAlertAdapter
from common.ingestion_types import IngestionSource, InvoiceMetadata
from services.invoice_ingestion_service import InvoiceIngestionService


def _metadata() -> InvoiceMetadata:
    return InvoiceMetadata(
        invoice_number="INV-200",
        supplier="Fabrikam",
        amount=100.0,
        invoice_date=datetime(2026, 2, 10),
    )


def test_service_saves_new_invoice_on_first_ingestion() -> None:
    repository = InMemoryIntakeRepositoryAdapter()
    alerts = NoopIngestionAlertAdapter()
    service = InvoiceIngestionService(intake_repository=repository, alert_port=alerts)

    invoice = service.ingest_ap_email_invoice(
        source_id="mail-1",
        metadata=_metadata(),
        file_hash="hash-1",
        processed_at=datetime(2026, 2, 11, 10, 0, 0),
    )

    assert invoice.dedupe_key == "inv-200|fabrikam|2026-02-10|100.00"
    assert len(invoice.history) == 1
    assert invoice.history[0].source == IngestionSource.AP_EMAIL


def test_service_appends_history_for_duplicate_ingestion() -> None:
    repository = InMemoryIntakeRepositoryAdapter()
    alerts = NoopIngestionAlertAdapter()
    service = InvoiceIngestionService(intake_repository=repository, alert_port=alerts)

    service.ingest_ap_email_invoice(
        source_id="mail-1",
        metadata=_metadata(),
        file_hash="hash-1",
        processed_at=datetime(2026, 2, 11, 10, 0, 0),
    )
    invoice = service.ingest_accounting_invoice(
        source_id="acct-1",
        metadata=_metadata(),
        file_hash="hash-2",
        processed_at=datetime(2026, 2, 11, 11, 0, 0),
    )

    assert len(invoice.history) == 2
    assert invoice.history[-1].source == IngestionSource.ACCOUNTING_SYSTEM


def test_service_records_failures_via_alert_port() -> None:
    repository = InMemoryIntakeRepositoryAdapter()
    alerts = NoopIngestionAlertAdapter()
    service = InvoiceIngestionService(intake_repository=repository, alert_port=alerts)

    service.record_ingestion_failure(
        source=IngestionSource.AP_EMAIL,
        error_type="integration_unavailable",
        occurred_at=datetime(2026, 2, 11, 12, 0, 0),
    )

    assert len(alerts.events) == 1
    assert alerts.events[0].error_type == "integration_unavailable"
