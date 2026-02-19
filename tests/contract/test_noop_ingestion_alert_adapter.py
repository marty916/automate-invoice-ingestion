from __future__ import annotations

from datetime import datetime

from adapters.noop_ingestion_alert_adapter import NoopIngestionAlertAdapter
from common.ingestion_types import IngestionSource


def test_noop_alert_adapter_records_alert_event_contract() -> None:
    adapter = NoopIngestionAlertAdapter()

    adapter.notify_failure(
        source=IngestionSource.ACCOUNTING_SYSTEM,
        error_type="upstream_error",
        occurred_at=datetime(2026, 2, 11, 14, 0, 0),
    )

    assert len(adapter.events) == 1
    assert adapter.events[0].source == IngestionSource.ACCOUNTING_SYSTEM
