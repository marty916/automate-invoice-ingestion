from __future__ import annotations

from typing import Sequence

from common.ingestion_types import SourceInvoicePayload
from ports.outbound.accounting_source_port import AccountingSourcePort


class AccountingSourceAdapter(AccountingSourcePort):
    def __init__(self, client: object) -> None:
        self._client = client

    def fetch_new_invoices(self) -> Sequence[SourceInvoicePayload]:
        raise NotImplementedError("Accounting integration is implemented in Increment 2")
