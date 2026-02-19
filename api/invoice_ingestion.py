from __future__ import annotations

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query

from adapters.in_memory_intake_repository_adapter import InMemoryIntakeRepositoryAdapter
from adapters.noop_ingestion_alert_adapter import NoopIngestionAlertAdapter
from api.dependencies.auth import UserContext, check_scope, get_current_user
from api.schemas.api_response import ApiResponse
from api.schemas.invoice_ingestion import (
    IngestionFailureResponse,
    IngestionHistoryEntryResponse,
    InvoiceIntakeItemResponse,
)
from common.ingestion_types import IngestionSource
from services.invoice_ingestion_service import InvoiceIngestionService

router = APIRouter(prefix="/v1", tags=["invoice-ingestion"])

_service = InvoiceIngestionService(
    intake_repository=InMemoryIntakeRepositoryAdapter(),
    alert_port=NoopIngestionAlertAdapter(),
)


def get_invoice_ingestion_service() -> InvoiceIngestionService:
    return _service


@router.get(
    "/invoices/intake",
    summary="List intake invoices for analysts",
    description="Returns intake queue items filtered by source and sorted by ingestion timestamp.",
)
def list_intake_invoices(
    _user: Annotated[UserContext, Depends(get_current_user)],
    _scope: Annotated[UserContext, Depends(check_scope("finance_analyst"))],
    service: Annotated[InvoiceIngestionService, Depends(get_invoice_ingestion_service)],
    source: Annotated[Literal["AP email",
                              "Accounting system"] | None, Query()] = None,
    sort: Annotated[Literal["asc", "desc"], Query()] = "desc",
) -> ApiResponse[list[InvoiceIntakeItemResponse]]:
    mapped_source = IngestionSource(source) if source else None
    newest_first = sort == "desc"
    items = service.list_for_analyst(
        source=mapped_source, newest_first=newest_first)

    response_items = [
        InvoiceIntakeItemResponse(
            dedupe_key=item.dedupe_key,
            invoice_number=item.metadata.invoice_number,
            supplier=item.metadata.supplier,
            amount=item.metadata.amount,
            invoice_date=item.metadata.invoice_date,
            file_hash=item.file_hash,
            history=[
                IngestionHistoryEntryResponse(
                    source=entry.source.value,
                    ingested_at=entry.ingested_at,
                    status=entry.status,
                )
                for entry in item.history
            ],
        )
        for item in items
    ]
    return ApiResponse(success=True, data=response_items)


@router.get(
    "/ingestion/status",
    summary="List ingestion failures for operations",
    description="Returns ingestion failure events for AP email and accounting sync.",
)
def list_ingestion_status(
    _user: Annotated[UserContext, Depends(get_current_user)],
    _scope: Annotated[UserContext, Depends(check_scope("finance_ops"))],
    service: Annotated[InvoiceIngestionService, Depends(get_invoice_ingestion_service)],
) -> ApiResponse[list[IngestionFailureResponse]]:
    failures = service.list_ingestion_failures()
    response_items = [
        IngestionFailureResponse(
            source=failure.source.value,
            error_type=failure.error_type,
            occurred_at=failure.occurred_at,
        )
        for failure in failures
    ]
    return ApiResponse(success=True, data=response_items)
