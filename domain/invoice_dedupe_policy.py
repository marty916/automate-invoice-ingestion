from __future__ import annotations

from typing import Optional

from common.ingestion_types import InvoiceMetadata


class InvoiceDedupePolicy:
    @staticmethod
    def build_dedupe_key(metadata: InvoiceMetadata, file_hash: Optional[str]) -> str:
        metadata_key = "|".join(
            [
                metadata.invoice_number.strip().lower(),
                metadata.supplier.strip().lower(),
                metadata.invoice_date.date().isoformat(),
                f"{metadata.amount:.2f}",
            ]
        )

        if metadata.invoice_number and metadata.supplier:
            return metadata_key

        if file_hash:
            return f"hash:{file_hash.strip().lower()}"

        return metadata_key
