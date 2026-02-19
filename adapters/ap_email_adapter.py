from __future__ import annotations

from typing import Protocol
from typing import Sequence

from common.ingestion_types import SourceInvoicePayload
from ports.outbound.ap_email_source_port import ApEmailSourcePort


class ApEmailClient(Protocol):
    def fetch_new_invoices(self) -> Sequence[SourceInvoicePayload]:
        ...


class ApEmailAdapter(ApEmailSourcePort):
    def __init__(self, client: ApEmailClient) -> None:
        self._client = client

    def fetch_new_invoices(self) -> Sequence[SourceInvoicePayload]:
        try:
            return self._client.fetch_new_invoices()
        except Exception as exc:
            raise RuntimeError("AP email source fetch failed") from exc
