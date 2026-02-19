# ADR-001: Invoice Ingestion Source Integration and Deduplication Contract

## Status
Accepted

## Date
2026-02-19

## Authors
- Marty Bradley

---

## 1. Context

The invoice ingestion feature in `features/invoice_ingestion` requires intake from AP email and accounting system sources, deduplication within and across sources, persistent ingestion history, analyst filtering/sorting, and operational visibility for ingestion failures from `features/invoice_ingestion/acceptance.feature`.

This decision must comply with layering and dependency constraints in `docs/architecture/ARCH_CONTRACT.md`, boundary and import rules in `docs/architecture/BOUNDARIES.md`, API conventions in `docs/architecture/API_CONVENTIONS.md`, and authentication/authorization patterns in `docs/architecture/SECURITY_AUTH_PATTERNS.md`.

Given ADR triggers in `docs/architecture/ARCH_CONTRACT.md` and `.github/copilot-instructions.md`, introducing source integration contracts and deduplication orchestration requires an ADR.

Reference:
- `features/invoice_ingestion/plan.md`
- Relevant sections of `ARCH_CONTRACT.md`
- Relevant boundary rules in `BOUNDARIES.md`

---

## 2. Decision

We will implement invoice ingestion using explicit inbound and outbound ports with adapter implementations per source, with deduplication and ingestion-history orchestration in the domain/service layer.

Duplicates are determined by invoice number + vendor + invoice date + amount, with optional file-hash fallback when metadata is incomplete.

All analyst and operations visibility endpoints will be versioned API routes that enforce JWT authentication and RBAC authorization before invoking ports, and return standardized response and error envelopes.

---

## 3. Architectural Impact

### 3.1 Boundaries
- Layers/services affected:
  - API adapters for ingestion-status and analyst query views
  - Inbound ports for ingestion and query use cases
  - Domain/services for dedupe, state transition, and history recording
  - Outbound ports/adapters for AP email source, accounting source, persistence, and alerting
- Dependency direction changes:
  - New outbound dependency edges from domain/service to source and persistence ports
  - No direct adapter-to-adapter or API-to-domain direct coupling outside ports
- New modules introduced:
  - Source ingestion ports/adapters
  - Deduplication policy component
  - Ingestion history/audit persistence contract

Confirm:
- No forbidden cross-layer access is introduced
- Dependency direction complies with `BOUNDARIES.md`

### 3.2 API Impact
If applicable:
- Route changes:
  - New/updated versioned endpoints for queue filtering/sorting and ingestion failure/status visibility
- Versioning impact:
  - All routes follow repository versioning conventions
- Error model impact:
  - Domain/service errors are mapped centrally to standard API error shape
- OpenAPI updates required:
  - Yes, if API surface changes are introduced

### 3.3 Security Impact
- Auth pattern used:
  - OAuth2/JWT bearer validation at API adapter boundary
- Authorization changes:
  - RBAC checks for `finance_analyst` and `finance_ops` roles on operational views/actions
- Token handling implications:
  - No raw token handling in domain/services
- Data classification considerations:
  - Invoice metadata and operational logs are sensitive business data
- Logging/redaction implications:
  - Structured logs include correlation identifiers and event metadata while excluding secrets/PII payloads

---

## 4. Alternatives Considered

For each alternative:

### Option A
- Description
  - Source-specific adapter logic directly performs dedupe and persistence
- Pros
  - Fewer initial abstractions
- Cons
  - Breaks layering intent, duplicates logic, hard to test, higher coupling
- Why rejected
  - Violates maintainability and boundary goals

### Option B
- Description
  - Central ingestion orchestrator in domain/service with source adapters behind ports
- Pros
  - Strong boundary compliance, testability, clear ownership of dedupe policy
- Cons
  - Requires more upfront interface design
- Why rejected
  - Not rejected; this is the selected approach

### Option C
- Description
  - File-hash-only dedupe strategy
- Pros
  - Simple deterministic check
- Cons
  - Misses semantically duplicate invoices with different binary representations
- Why rejected
  - Lower business accuracy than metadata-first strategy with hash fallback

---

## 5. Evaluation Impact

Does this decision affect:

- LLM evaluation criteria?
  - No
- Deterministic evaluation checks?
  - Yes
- CI enforcement rules?
  - Yes

If yes:
- List affected criteria from `features/<feature_name>/eval_criteria.yaml`
  - Duplicate prevention within and across sources
  - Ingestion latency and reliability thresholds
  - Failure visibility and operational status behavior
- Describe changes required
  - Maintain schema-compliant deterministic criteria in `features/invoice_ingestion/eval_criteria.yaml` and ensure CI evaluator mappings are implemented for each eval_class

---

## 6. Risks and Tradeoffs

- Technical risks:
  - Dedupe false positives/negatives
- Operational risks:
  - Retry/backoff tuning may affect queue freshness and on-call noise
- Security risks:
  - Accidental exposure of sensitive invoice metadata in logs
- Performance implications:
  - Cross-source dedupe checks may increase processing time

Mitigations:
- Deterministic dedupe test matrix with edge-case fixtures
- Bounded retries with explicit dead-letter/error states and alerts
- Structured logging policy with redaction checks
- Performance budget tests for ingestion window compliance

---

## 7. Plan Alignment

Reference:

- Feature plan increments impacted:
  - Increment 1: Port contracts, source adapter scaffolding, dedupe policy contract
  - Increment 2: Ingestion orchestration, history persistence, failure state handling
  - Increment 3: Analyst/ops API surface, authz enforcement, observability
  - Increment 4: Evaluation gates, quality/security checks, release readiness
- New increment required?
  - No
- Scope adjustments required?
  - `features/invoice_ingestion/plan.md` must include deterministic evaluation criteria completion and API/contract validation tasks

If the decision changes scope:
- `plan.md` must be updated.

---

## 8. Consequences

### Positive
- Clear architectural separation and testability
- Consistent dedupe behavior across sources
- Better operational visibility and governance alignment

### Negative
- Higher upfront design effort for ports and contracts
- More integration test surface area

### Neutral
- Does not change product scope; formalizes delivery structure and constraints

---

## 9. Follow-Up Actions

- Code changes required:
  - Implement ports/adapters, orchestration, dedupe policy, history persistence, and status/query API endpoints
- Documentation updates required:
  - Finalize `features/invoice_ingestion/architecture_preflight.md` and keep `features/invoice_ingestion/plan.md` aligned
- CI updates required:
  - Add deterministic evaluation criteria and ensure boundary/security/quality gates are wired
- Security review required:
  - Validate RBAC enforcement, token handling, and log redaction behavior

---

## 10. Approval

Approved by:
- Architect:
- Security (if applicable):
- Product (if scope impact):
