from __future__ import annotations

from datetime import datetime

from adapters.in_memory_intake_repository_adapter import InMemoryIntakeRepositoryAdapter
from adapters.noop_ingestion_alert_adapter import NoopIngestionAlertAdapter
from services.invoice_ingestion_service import InvoiceIngestionService


def before_scenario(context, scenario) -> None:
    context.repository = InMemoryIntakeRepositoryAdapter()
    context.alerts = NoopIngestionAlertAdapter()
    context.service = InvoiceIngestionService(
        intake_repository=context.repository, alert_port=context.alerts)
    context.ap_email_connected = True
    context.accounting_connected = True
    context.pending_ap_email = []
    context.pending_accounting = []
    context.last_ingested_invoice = None
    context.last_processed_at = datetime(2026, 2, 19, 9, 0, 0)
    context.last_queue_count_before = 0
    context.last_queue_count_after = 0
    context.failure_logs = []
