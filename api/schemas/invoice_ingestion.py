from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class IngestionHistoryEntryResponse(BaseModel):
    source: Literal["AP email", "Accounting system"]
    ingested_at: datetime
    status: str


class InvoiceIntakeItemResponse(BaseModel):
    dedupe_key: str
    invoice_number: str
    supplier: str
    amount: float
    invoice_date: datetime
    file_hash: str | None
    history: list[IngestionHistoryEntryResponse]


class IngestionFailureResponse(BaseModel):
    source: Literal["AP email", "Accounting system"]
    error_type: str
    occurred_at: datetime
