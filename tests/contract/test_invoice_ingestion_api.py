from __future__ import annotations

from datetime import datetime

from fastapi.testclient import TestClient

from adapters.in_memory_intake_repository_adapter import InMemoryIntakeRepositoryAdapter
from adapters.noop_ingestion_alert_adapter import NoopIngestionAlertAdapter
from api.invoice_ingestion import get_invoice_ingestion_service
from common.ingestion_types import IngestionSource, InvoiceMetadata
from main import app
from services.invoice_ingestion_service import InvoiceIngestionService


def _build_service_with_seed_data() -> InvoiceIngestionService:
    repository = InMemoryIntakeRepositoryAdapter()
    alerts = NoopIngestionAlertAdapter()
    service = InvoiceIngestionService(
        intake_repository=repository, alert_port=alerts)

    service.ingest_ap_email_invoice(
        source_id="mail-1",
        metadata=InvoiceMetadata(
            invoice_number="INV-API-1",
            supplier="Contoso",
            amount=100.0,
            invoice_date=datetime(2026, 2, 10),
        ),
        file_hash="hash-api-1",
        processed_at=datetime(2026, 2, 19, 9, 0, 0),
    )
    service.ingest_accounting_invoice(
        source_id="acct-1",
        metadata=InvoiceMetadata(
            invoice_number="INV-API-2",
            supplier="Fabrikam",
            amount=200.0,
            invoice_date=datetime(2026, 2, 11),
        ),
        file_hash="hash-api-2",
        processed_at=datetime(2026, 2, 19, 10, 0, 0),
    )
    service.record_ingestion_failure(
        source=IngestionSource.AP_EMAIL,
        error_type="integration_unavailable",
        occurred_at=datetime(2026, 2, 19, 11, 0, 0),
    )
    return service


def _client(service: InvoiceIngestionService) -> TestClient:
    app.dependency_overrides[get_invoice_ingestion_service] = lambda: service
    return TestClient(app)


def _headers(scopes: str) -> dict[str, str]:
    return {"X-User-Id": "user-1", "X-Scopes": scopes}


def test_list_intake_requires_authentication() -> None:
    client = _client(_build_service_with_seed_data())

    response = client.get("/v1/invoices/intake")

    assert response.status_code == 401


def test_list_intake_requires_finance_analyst_scope() -> None:
    client = _client(_build_service_with_seed_data())

    response = client.get("/v1/invoices/intake",
                          headers=_headers("finance_ops"))

    assert response.status_code == 403


def test_list_intake_filters_by_source_and_sorts_desc() -> None:
    client = _client(_build_service_with_seed_data())

    response = client.get(
        "/v1/invoices/intake",
        params={"source": "AP email", "sort": "desc"},
        headers=_headers("finance_analyst,finance_ops"),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert len(body["data"]) == 1
    assert body["data"][0]["history"][-1]["source"] == "AP email"


def test_status_endpoint_requires_finance_ops_scope() -> None:
    client = _client(_build_service_with_seed_data())

    response = client.get("/v1/ingestion/status",
                          headers=_headers("finance_analyst"))

    assert response.status_code == 403


def test_status_endpoint_returns_failure_events() -> None:
    client = _client(_build_service_with_seed_data())

    response = client.get("/v1/ingestion/status",
                          headers=_headers("finance_ops"))

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert len(body["data"]) == 1
    assert body["data"][0]["error_type"] == "integration_unavailable"
