Feature: Invoice ingestion into intake queue

Scenario: Invoices sent to AP email are ingested into the intake queue with source and timestamp
  Given a supplier sends an email with a valid invoice attachment to the AP inbox
    And the AP email integration is connected and healthy
  When the system processes new messages in the AP inbox
  Then a new invoice record is created in the intake queue
    And the invoice record includes the attached invoice file
    And the invoice record has ingestion source set to "AP email"
    And the invoice record has an ingestion timestamp set to the time of processing

Scenario: New invoices in the accounting system are synced into the intake queue with source and timestamp
  Given a new invoice exists in the accounting system
    And the accounting integration has access to that invoice
  When the scheduled or triggered sync runs
  Then a new invoice record is created in the intake queue
    And the invoice record includes core invoice metadata (e.g., invoice number, supplier, amount, date)
    And the invoice record has ingestion source set to "Accounting system"
    And the invoice record has an ingestion timestamp set to the time of sync

Scenario: Duplicate invoices from the same source are not duplicated in the intake queue
  Given an invoice has already been ingested from the AP email inbox
    And a second email arrives with the same invoice file and matching core metadata
  When the system processes the second email
  Then the system does not create a second invoice record in the intake queue
    And the existing invoice record is updated or annotated to indicate a duplicate email was received
    And the event is captured for monitoring or audit purposes

Scenario: Invoices received from email and accounting system are de-duplicated
  Given an invoice was previously ingested from the AP email inbox into the intake queue
    And the same invoice is later created in the accounting system with matching core metadata
  When the accounting system sync runs
  Then the system does not create a separate duplicate invoice record
    And the existing invoice record is updated to reflect that it is seen in both sources
    And the ingestion history shows both "AP email" and "Accounting system" with their respective timestamps

Scenario: Financial Analyst filters the intake queue by ingestion source and timestamp
  Given multiple invoices exist in the intake queue from both email and the accounting system
    And each invoice has ingestion source and ingestion timestamp recorded
  When a Financial Analyst opens the intake queue view
    And filters invoices by ingestion source = "AP email"
    And sorts invoices by ingestion timestamp descending
  Then only invoices ingested from the AP email inbox are displayed
    And the most recently ingested invoices appear at the top of the list
    And the Analyst can see the ingestion source and timestamp for each invoice

Scenario: AP email ingestion failure is surfaced for investigation
  Given the AP email integration is misconfigured or temporarily unavailable
    And a supplier sends an email with a valid invoice attachment to the AP inbox
  When the system attempts to process new messages in the AP inbox
  Then the invoice is not added to the intake queue
    And the failure is logged with error details
    And an alert or status indicator is available to operations or Finance
    And there is a way for an authorized user to see that email ingestion is failing so they can take corrective action

Scenario: Accounting system invoice sync failure is surfaced for investigation
  Given the accounting system integration is unavailable or returns an error for new invoices
    And a new invoice exists in the accounting system
  When the scheduled or triggered sync runs
  Then the invoice is not added to the intake queue
    And the failure is logged with error details
    And an alert or status indicator is available to operations or Finance
    And there is a way for an authorized user to see that accounting ingestion is failing so they can take corrective action