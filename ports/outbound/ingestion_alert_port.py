from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Sequence

from common.ingestion_types import IngestionSource


class IngestionFailureEvent:
    def __init__(self, source: IngestionSource, error_type: str, occurred_at: datetime) -> None:
        self.source = source
        self.error_type = error_type
        self.occurred_at = occurred_at


class IngestionAlertPort(ABC):
    @abstractmethod
    def notify_failure(self, source: IngestionSource, error_type: str, occurred_at: datetime) -> None:
        raise NotImplementedError

    @abstractmethod
    def list_failures(self) -> Sequence[IngestionFailureEvent]:
        raise NotImplementedError
