from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from common.ingestion_types import SourceInvoicePayload


class ApEmailSourcePort(ABC):
    @abstractmethod
    def fetch_new_invoices(self) -> Sequence[SourceInvoicePayload]:
        raise NotImplementedError
