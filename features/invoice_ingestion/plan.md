# Feature Plan: invoice_ingestion

## Objective
- Deliver reliable multi-source invoice ingestion into one intake queue with deterministic deduplication and auditable ingestion history.
- Enable Finance/Operations users to monitor ingestion status and analysts to filter/sort by source and timestamp.

## Scope Boundaries
### In scope
- AP email ingestion and accounting source sync into intake queue.
- Deduplication within source and across sources.
- Ingestion history tracking (source, timestamp, status).
- Analyst queue filtering by source and sorting by ingestion timestamp.
- Failure logging and operational status visibility for authorized users.

### Out of scope
- Invoice extraction/classification beyond core metadata ingestion.
- Approval workflows, downstream posting, or payment orchestration.
- UI redesign beyond required analyst/ops visibility behavior.

### Assumptions
- Roles are `finance_analyst` and `finance_ops`.
- Ingestion history retention target is 24 months.
- Deterministic evaluation mode is required.
- OpenAPI artifacts will be updated when API surface changes.

## Architecture Alignment
### Relevant contracts
- docs/architecture/ARCH_CONTRACT.md: layering, boundaries, ADR triggers, observability, testing policy.
- docs/architecture/BOUNDARIES.md: allowed dependencies, communication rules, enforcement.
- docs/architecture/API_CONVENTIONS.md: versioning, response envelope, error model, observability, API tests.
- docs/architecture/SECURITY_AUTH_PATTERNS.md: JWT authn, RBAC authz, token handling, identity propagation.

### ADRs
- New ADRs required:
	- ADR-001: Invoice Ingestion Source Integration and Deduplication Contract
- Existing ADRs referenced:
	- None currently

### Interfaces and dependencies
- Services/APIs touched:
	- Intake queue ingestion API/use case.
	- Analyst query/status API endpoints.
	- Source connector interfaces for AP email and accounting sync.
- Data stores/events touched:
	- Invoice intake records.
	- Ingestion history/audit records.
	- Failure/alert status records.
- External dependencies:
	- AP email integration endpoint/service.
	- Accounting system integration endpoint/service.
	- Alerting/monitoring channel.

### Security and compliance
- AuthN/AuthZ considerations:
	- JWT validation at adapter entry points; RBAC checks for `finance_analyst` and `finance_ops`.
- Data classification and PII handling:
	- Invoice content and metadata treated as sensitive; no secrets/PII in logs.
- Threats and mitigations:
	- Unauthorized access mitigated by enforced RBAC and endpoint guards.
	- Sensitive data leakage mitigated by structured redacted logging.
	- Integration outage risk mitigated by explicit failure states and operational visibility.

## Increments

### Increment 1: Contracts and scaffolding
**Goal**
- Establish architecture-safe interfaces and baseline components for source ingestion and dedup policy.

**Deliverables**
- Inbound/outbound port definitions for ingestion, persistence, and source retrieval.
- Adapter scaffolding for AP email and accounting integrations.
- Canonical deduplication contract and history/status model draft.
- Updated/created ADR link in feature artifacts.

**Implementation notes**
- Keep dependency direction strictly adapter -> port -> service/domain.
- No adapter-to-adapter coupling; no domain dependency on infrastructure SDK types.

**Tests**
- Unit:
	- Dedup key rule tests and model validation tests.
- Integration:
	- Basic adapter connectivity stubs/mocks for both sources.
- Contract:
	- Port contract tests for source and persistence interfaces.

**Evaluation impact**
- LLM eval required? (yes/no)
	- no
- If yes, criteria names impacted:
	- n/a
- If no, rationale:
	- Feature uses deterministic evaluation mode.

**Definition of Done**
- Interfaces and baseline contracts compile and pass boundary checks.
- ADR reference and architecture alignment are explicit in feature artifacts.

### Increment 2: Ingestion orchestration and dedup execution
**Goal**
- Implement end-to-end ingestion flow with deterministic deduplication and history persistence.

**Deliverables**
- Orchestration flow for AP email ingestion and accounting sync ingestion.
- Dedup processing across same-source and cross-source events.
- Ingestion history persistence for source, timestamp, and high-level status.

**Implementation notes**
- Preserve idempotency and clear source provenance.
- Ensure duplicate events annotate existing records without duplicate queue creation.

**Tests**
- Unit:
	- Orchestration decision logic and duplicate annotation behavior.
- Integration:
	- Source-to-intake flow tests for both integrations.
- Contract:
	- Persistence contract tests for queue and history updates.

**Evaluation impact**
- LLM eval required? (yes/no)
	- no
- If yes, criteria names impacted:
	- n/a
- If no, rationale:
	- Deterministic pass/fail checks validate dedup and ingestion behavior.

**Definition of Done**
- Acceptance scenarios for ingestion and dedup pass.
- Ingestion history correctness is verified in automated tests.

### Increment 3: Analyst/ops visibility and failure surfacing
**Goal**
- Expose required analyst filtering/sorting and operational failure visibility with secure access control.

**Deliverables**
- API endpoints for ingestion source filtering and timestamp sorting.
- API/status surface for ingestion failure visibility and investigation.
- Structured failure logging with source, time, and error type.
- Alert/status integration for operations/Finance monitoring.

**Implementation notes**
- Apply API response envelope and centralized error mapping.
- Enforce authn/authz before port invocation on all endpoints.

**Tests**
- Unit:
	- Authorization and filter/sort logic tests.
- Integration:
	- End-to-end failure surfacing for AP email and accounting sync outages.
- Contract:
	- API contract tests for response shape, status codes, and error model.

**Evaluation impact**
- LLM eval required? (yes/no)
	- no
- If yes, criteria names impacted:
	- n/a
- If no, rationale:
	- Deterministic checks cover endpoint behavior and failure-path assertions.

**Definition of Done**
- Analyst and ops acceptance scenarios pass with correct role-based access.
- Failure visibility and logging requirements are validated.

### Increment 4: NFR hardening and release gates
**Goal**
- Prove NFR compliance and complete CI quality/security/evaluation gates.

**Deliverables**
- Deterministic evaluation criteria finalized and wired in CI.
- Reliability, latency, and throughput verification artifacts.
- Security/compliance checks for encryption assumptions and auditability.
- Final documentation updates across feature artifacts and API contracts.

**Implementation notes**
- Align all thresholds to NFR targets and observable metrics.
- Keep changes scoped to this feature and required governance artifacts.

**Tests**
- Unit:
	- Edge-case and resilience unit scenarios.
- Integration:
	- Throughput and latency validation under representative load.
- Contract:
	- Final API and port contract conformance checks.

**Evaluation impact**
- LLM eval required? (yes/no)
	- no
- If yes, criteria names impacted:
	- n/a
- If no, rationale:
	- Deterministic mode with explicit thresholds and criteria.

**Definition of Done**
- NFR targets are met or documented with approved exception.
- CI gates pass for tests, quality, boundary enforcement, security, and evaluation.

## Risks
- Risk:
	- Dedupe false positives or false negatives.
	- Impact:
		- Incorrect queue state and analyst confusion.
	- Mitigation:
		- Deterministic dedupe test matrix with representative fixtures.
- Risk:
	- Source integration outages create ingestion backlog.
	- Impact:
		- SLA miss and delayed invoice processing.
	- Mitigation:
		- Explicit failure state tracking, alerting, and retry/backoff policy tests.
- Risk:
	- Logging exposes sensitive invoice metadata.
	- Impact:
		- Security/compliance violation.
	- Mitigation:
		- Redaction policy checks and structured logging guardrails.
- Risk:
	- Eval harness-to-criterion mapping may be incomplete.
	- Impact:
		- CI eval gate may fail despite correct feature behavior.
	- Mitigation:
		- Maintain schema-compliant criteria and add/verify evaluator mappings in CI.

## Definition of Done (Feature-Level)
- Acceptance criteria satisfied (features/<feature>/acceptance.feature)
- NFRs satisfied (features/<feature>/nfrs.md)
- Evaluation criteria satisfied (features/<feature>/eval_criteria.yaml)
- CI passes (tests, quality, eval gates)
- ADRs updated/added (docs/architecture/ADR/)
- PR includes links to plan/spec artifacts
