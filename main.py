from __future__ import annotations

from fastapi import FastAPI

from api.invoice_ingestion import router as invoice_ingestion_router

app = FastAPI(title="Automate Invoice Ingestion", version="0.1.0")
app.include_router(invoice_ingestion_router)
