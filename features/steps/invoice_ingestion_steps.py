from __future__ import annotations

from datetime import datetime

from behave import given, then, when

from common.ingestion_types import IngestionSource, InvoiceMetadata


def _queue_count(context) -> int:
    return len(context.repository.list_by_source_sorted(source=None, newest_first=True))


def _sample_metadata(invoice_number: str = "INV-001") -> InvoiceMetadata:
    return InvoiceMetadata(
        invoice_number=invoice_number,
        supplier="Contoso",
        amount=125.0,
        invoice_date=datetime(2026, 2, 1),
    )


@given("a supplier sends an email with a valid invoice attachment to the AP inbox")
def given_ap_email_arrives(context) -> None:
    context.pending_ap_email.append(
        {
            "source_id": f"mail-{len(context.pending_ap_email) + 1}",
            "metadata": _sample_metadata("INV-EMAIL-1"),
            "file_hash": "hash-email-1",
        }
    )


@given("the AP email integration is connected and healthy")
def given_ap_email_healthy(context) -> None:
    context.ap_email_connected = True


@when("the system processes new messages in the AP inbox")
@when("the system attempts to process new messages in the AP inbox")
@when("the system processes the second email")
def when_process_ap_email(context) -> None:
    context.last_queue_count_before = _queue_count(context)
    context.last_ingested_invoice = None
    if not context.ap_email_connected:
        context.failure_logs.append(
            {"source": "AP email", "error_type": "integration_unavailable"})
        context.service.record_ingestion_failure(
            source=IngestionSource.AP_EMAIL,
            error_type="integration_unavailable",
            occurred_at=context.last_processed_at,
        )
        context.last_queue_count_after = _queue_count(context)
        return

    for payload in context.pending_ap_email:
        context.last_ingested_invoice = context.service.ingest_ap_email_invoice(
            source_id=payload["source_id"],
            metadata=payload["metadata"],
            file_hash=payload["file_hash"],
            processed_at=context.last_processed_at,
        )
    context.pending_ap_email = []
    context.last_queue_count_after = _queue_count(context)


@then("a new invoice record is created in the intake queue")
def then_invoice_record_created(context) -> None:
    assert context.last_ingested_invoice is not None
    assert context.last_queue_count_after == context.last_queue_count_before + 1


@then("the invoice record includes the attached invoice file")
def then_attached_file_present(context) -> None:
    assert context.last_ingested_invoice.file_hash is not None


@then('the invoice record has ingestion source set to "{source_name}"')
def then_invoice_source_set(context, source_name: str) -> None:
    assert context.last_ingested_invoice is not None
    assert context.last_ingested_invoice.history[-1].source.value == source_name


@then("the invoice record has an ingestion timestamp set to the time of processing")
@then("the invoice record has an ingestion timestamp set to the time of sync")
def then_invoice_timestamp_set(context) -> None:
    assert context.last_ingested_invoice is not None
    assert context.last_ingested_invoice.history[-1].ingested_at == context.last_processed_at


@given("a new invoice exists in the accounting system")
def given_accounting_invoice_exists(context) -> None:
    context.pending_accounting.append(
        {
            "source_id": f"acct-{len(context.pending_accounting) + 1}",
            "metadata": _sample_metadata("INV-ACCT-1"),
            "file_hash": "hash-acct-1",
        }
    )


@given("the accounting integration has access to that invoice")
def given_accounting_access(context) -> None:
    context.accounting_connected = True


@when("the scheduled or triggered sync runs")
@when("the accounting system sync runs")
def when_accounting_sync_runs(context) -> None:
    context.last_queue_count_before = _queue_count(context)
    context.last_ingested_invoice = None
    if not context.accounting_connected:
        context.failure_logs.append(
            {"source": "Accounting system", "error_type": "integration_unavailable"})
        context.service.record_ingestion_failure(
            source=IngestionSource.ACCOUNTING_SYSTEM,
            error_type="integration_unavailable",
            occurred_at=context.last_processed_at,
        )
        context.last_queue_count_after = _queue_count(context)
        return

    for payload in context.pending_accounting:
        context.last_ingested_invoice = context.service.ingest_accounting_invoice(
            source_id=payload["source_id"],
            metadata=payload["metadata"],
            file_hash=payload["file_hash"],
            processed_at=context.last_processed_at,
        )
    context.pending_accounting = []
    context.last_queue_count_after = _queue_count(context)


@then("the invoice record includes core invoice metadata (e.g., invoice number, supplier, amount, date)")
def then_core_metadata_present(context) -> None:
    assert context.last_ingested_invoice is not None
    assert context.last_ingested_invoice.metadata.invoice_number
    assert context.last_ingested_invoice.metadata.supplier


@given("an invoice has already been ingested from the AP email inbox")
def given_invoice_already_ingested_from_ap(context) -> None:
    context.service.ingest_ap_email_invoice(
        source_id="mail-initial",
        metadata=_sample_metadata("INV-DUP-1"),
        file_hash="hash-dup",
        processed_at=context.last_processed_at,
    )


@given("a second email arrives with the same invoice file and matching core metadata")
def given_second_duplicate_email_arrives(context) -> None:
    context.pending_ap_email = [
        {
            "source_id": "mail-duplicate",
            "metadata": _sample_metadata("INV-DUP-1"),
            "file_hash": "hash-dup",
        }
    ]


@then("the system does not create a second invoice record in the intake queue")
def then_no_duplicate_record_created(context) -> None:
    assert context.last_queue_count_after == context.last_queue_count_before


@then("the existing invoice record is updated or annotated to indicate a duplicate email was received")
def then_existing_record_annotated_duplicate(context) -> None:
    assert context.last_ingested_invoice is not None
    assert context.last_ingested_invoice.history[-1].status.startswith(
        "duplicate_seen")


@then("the event is captured for monitoring or audit purposes")
def then_event_captured_for_audit(context) -> None:
    assert context.last_ingested_invoice is not None
    assert len(context.last_ingested_invoice.history) >= 2


@given("an invoice was previously ingested from the AP email inbox into the intake queue")
def given_previously_ingested_email_invoice(context) -> None:
    context.service.ingest_ap_email_invoice(
        source_id="mail-cross-source",
        metadata=_sample_metadata("INV-CROSS-1"),
        file_hash="hash-cross",
        processed_at=context.last_processed_at,
    )


@given("the same invoice is later created in the accounting system with matching core metadata")
def given_same_invoice_in_accounting(context) -> None:
    context.pending_accounting = [
        {
            "source_id": "acct-cross-source",
            "metadata": _sample_metadata("INV-CROSS-1"),
            "file_hash": "hash-cross-acct",
        }
    ]


@then("the system does not create a separate duplicate invoice record")
def then_no_separate_duplicate_invoice(context) -> None:
    assert context.last_queue_count_after == context.last_queue_count_before


@then("the existing invoice record is updated to reflect that it is seen in both sources")
def then_record_reflects_both_sources(context) -> None:
    assert context.last_ingested_invoice is not None
    sources = {event.source for event in context.last_ingested_invoice.history}
    assert IngestionSource.AP_EMAIL in sources
    assert IngestionSource.ACCOUNTING_SYSTEM in sources


@then('the ingestion history shows both "AP email" and "Accounting system" with their respective timestamps')
def then_ingestion_history_shows_both_sources(context) -> None:
    assert context.last_ingested_invoice is not None
    assert len(context.last_ingested_invoice.history) >= 2
    assert all(
        event.ingested_at is not None for event in context.last_ingested_invoice.history)


@given("multiple invoices exist in the intake queue from both email and the accounting system")
def given_multiple_invoices_exist(context) -> None:
    context.service.ingest_ap_email_invoice(
        source_id="mail-filter-1",
        metadata=_sample_metadata("INV-FILTER-AP-1"),
        file_hash="hash-filter-ap-1",
        processed_at=datetime(2026, 2, 19, 10, 0, 0),
    )
    context.service.ingest_accounting_invoice(
        source_id="acct-filter-1",
        metadata=_sample_metadata("INV-FILTER-ACCT-1"),
        file_hash="hash-filter-acct-1",
        processed_at=datetime(2026, 2, 19, 11, 0, 0),
    )


@given("each invoice has ingestion source and ingestion timestamp recorded")
def given_invoice_source_and_timestamp_recorded(context) -> None:
    invoices = context.repository.list_by_source_sorted(source=None)
    assert len(invoices) >= 2
    assert all(invoice.history for invoice in invoices)


@when("a Financial Analyst opens the intake queue view")
def when_analyst_opens_queue(context) -> None:
    context.filtered_invoices = list(
        context.service.list_for_analyst(source=None, newest_first=True))


@when('filters invoices by ingestion source = "AP email"')
def when_filter_by_ap_email_source(context) -> None:
    context.filtered_invoices = list(context.service.list_for_analyst(
        source=IngestionSource.AP_EMAIL, newest_first=True))


@when("sorts invoices by ingestion timestamp descending")
def when_sort_by_timestamp_desc(context) -> None:
    context.filtered_invoices = list(context.service.list_for_analyst(
        source=IngestionSource.AP_EMAIL, newest_first=True))


@then("only invoices ingested from the AP email inbox are displayed")
def then_only_ap_email_displayed(context) -> None:
    assert context.filtered_invoices
    for invoice in context.filtered_invoices:
        assert any(event.source ==
                   IngestionSource.AP_EMAIL for event in invoice.history)


@then("the most recently ingested invoices appear at the top of the list")
def then_most_recent_first(context) -> None:
    timestamps = [max(event.ingested_at for event in invoice.history)
                  for invoice in context.filtered_invoices]
    assert timestamps == sorted(timestamps, reverse=True)


@then("the Analyst can see the ingestion source and timestamp for each invoice")
def then_analyst_can_see_source_and_timestamp(context) -> None:
    assert all(
        invoice.history and invoice.history[-1].ingested_at for invoice in context.filtered_invoices)


@given("the AP email integration is misconfigured or temporarily unavailable")
def given_ap_email_unavailable(context) -> None:
    context.ap_email_connected = False


@then("the invoice is not added to the intake queue")
def then_invoice_not_added(context) -> None:
    assert context.last_queue_count_after == context.last_queue_count_before


@then("the failure is logged with error details")
def then_failure_logged(context) -> None:
    assert context.failure_logs
    assert "error_type" in context.failure_logs[-1]


@then("an alert or status indicator is available to operations or Finance")
def then_alert_available(context) -> None:
    assert context.alerts.events


@then("there is a way for an authorized user to see that email ingestion is failing so they can take corrective action")
@then("there is a way for an authorized user to see that accounting ingestion is failing so they can take corrective action")
def then_authorized_user_can_see_failure(context) -> None:
    assert context.alerts.events


@given("the accounting system integration is unavailable or returns an error for new invoices")
def given_accounting_unavailable(context) -> None:
    context.accounting_connected = False
