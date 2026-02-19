from __future__ import annotations

from typing import Protocol
from typing import Sequence

from common.ingestion_types import SourceInvoicePayload
from ports.outbound.accounting_source_port import AccountingSourcePort


class AccountingClient(Protocol):
    def fetch_new_invoices(self) -> Sequence[SourceInvoicePayload]:
        ...


class AccountingSourceAdapter(AccountingSourcePort):
    def __init__(self, client: AccountingClient) -> None:
        self._client = client

    def fetch_new_invoices(self) -> Sequence[SourceInvoicePayload]:
        try:
            return self._client.fetch_new_invoices()
        except Exception as exc:
            raise RuntimeError("Accounting source fetch failed") from exc
