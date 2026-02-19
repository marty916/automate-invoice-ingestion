from __future__ import annotations

from datetime import datetime

from adapters.in_memory_intake_repository_adapter import InMemoryIntakeRepositoryAdapter
from common.ingestion_types import IngestedInvoice, IngestionSource, InvoiceMetadata


def test_in_memory_repository_round_trip_contract() -> None:
    repository = InMemoryIntakeRepositoryAdapter()
    metadata = InvoiceMetadata(
        invoice_number="INV-300",
        supplier="Northwind",
        amount=55.0,
        invoice_date=datetime(2026, 2, 9),
    )
    invoice = IngestedInvoice(dedupe_key="inv-300|northwind|2026-02-09|55.00", metadata=metadata, file_hash=None)

    repository.save_new(invoice)
    saved = repository.find_by_dedupe_key(invoice.dedupe_key)

    assert saved is not None
    repository.append_history(invoice.dedupe_key, IngestionSource.AP_EMAIL, datetime(2026, 2, 9, 9, 0, 0), "ingested")
    listed = repository.list_by_source_sorted(IngestionSource.AP_EMAIL)
    assert len(listed) == 1
