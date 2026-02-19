from __future__ import annotations

from datetime import datetime

import pytest

from adapters.accounting_source_adapter import AccountingSourceAdapter
from adapters.ap_email_adapter import ApEmailAdapter
from common.ingestion_types import InvoiceMetadata, SourceInvoicePayload


class FakeClient:
    def __init__(self, payloads: list[SourceInvoicePayload]) -> None:
        self._payloads = payloads

    def fetch_new_invoices(self) -> list[SourceInvoicePayload]:
        return list(self._payloads)


class FailingClient:
    def fetch_new_invoices(self) -> list[SourceInvoicePayload]:
        raise ValueError("upstream failed")


def _payload() -> SourceInvoicePayload:
    return SourceInvoicePayload(
        source_id="source-1",
        metadata=InvoiceMetadata(
            invoice_number="INV-500",
            supplier="Northwind",
            amount=55.0,
            invoice_date=datetime(2026, 2, 9),
        ),
        file_hash="hash-500",
        received_at=datetime(2026, 2, 19, 11, 0, 0),
    )


def test_ap_email_adapter_returns_client_payloads() -> None:
    adapter = ApEmailAdapter(client=FakeClient([_payload()]))

    results = adapter.fetch_new_invoices()

    assert len(results) == 1
    assert results[0].source_id == "source-1"


def test_accounting_source_adapter_returns_client_payloads() -> None:
    adapter = AccountingSourceAdapter(client=FakeClient([_payload()]))

    results = adapter.fetch_new_invoices()

    assert len(results) == 1
    assert results[0].source_id == "source-1"


def test_ap_email_adapter_wraps_client_failures() -> None:
    adapter = ApEmailAdapter(client=FailingClient())

    with pytest.raises(RuntimeError, match="AP email source fetch failed"):
        adapter.fetch_new_invoices()


def test_accounting_source_adapter_wraps_client_failures() -> None:
    adapter = AccountingSourceAdapter(client=FailingClient())

    with pytest.raises(RuntimeError, match="Accounting source fetch failed"):
        adapter.fetch_new_invoices()
