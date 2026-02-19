class InvoiceIngestionError(Exception):
    pass


class IngestionFailureError(InvoiceIngestionError):
    def __init__(self, source: str, error_type: str) -> None:
        super().__init__(f"Ingestion failed for source={source}, error_type={error_type}")
        self.source = source
        self.error_type = error_type
