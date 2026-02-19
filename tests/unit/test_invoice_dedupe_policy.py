from __future__ import annotations

from datetime import datetime

from common.ingestion_types import InvoiceMetadata
from domain.invoice_dedupe_policy import InvoiceDedupePolicy


def test_build_dedupe_key_uses_core_metadata() -> None:
    metadata = InvoiceMetadata(
        invoice_number="INV-100",
        supplier="Contoso",
        amount=42.5,
        invoice_date=datetime(2026, 2, 1),
    )

    result = InvoiceDedupePolicy.build_dedupe_key(metadata=metadata, file_hash="ABCD")

    assert result == "inv-100|contoso|2026-02-01|42.50"


def test_build_dedupe_key_falls_back_to_hash_when_metadata_is_partial() -> None:
    metadata = InvoiceMetadata(
        invoice_number="",
        supplier="",
        amount=42.5,
        invoice_date=datetime(2026, 2, 1),
    )

    result = InvoiceDedupePolicy.build_dedupe_key(metadata=metadata, file_hash="ABCD")

    assert result == "hash:abcd"
