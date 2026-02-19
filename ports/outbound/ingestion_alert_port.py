from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from common.ingestion_types import IngestionSource


class IngestionAlertPort(ABC):
    @abstractmethod
    def notify_failure(self, source: IngestionSource, error_type: str, occurred_at: datetime) -> None:
        raise NotImplementedError
