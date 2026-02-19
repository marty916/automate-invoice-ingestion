# Architecture Preflight: invoice_ingestion

This document validates architectural, security, and evaluation alignment
before implementation begins.

Preflight is required once per feature and must be updated if scope materially changes.

---

## 1. Artifact Review

- Feature folder: `features/invoice_ingestion/`
- acceptance.feature reviewed: yes
- nfrs.md reviewed: yes
- eval_criteria.yaml reviewed: yes
- plan.md exists: yes

Required artifacts are present.

---

## 2. Standards Referenced

Referenced standards and sections:

- `docs/architecture/ARCH_CONTRACT.md`
	- 2. Layering
	- 3. Boundaries
	- 5. ADR Rules
	- 7. Security
	- 8. Observability
	- 9. Testing Policy
- `docs/architecture/BOUNDARIES.md`
	- 2. Allowed Dependencies
	- 3. Communication Rules
	- 6. Enforcement
- `docs/architecture/API_CONVENTIONS.md`
	- 2. HTTP Verbs & Status Codes
	- 3. Request & Response Format
	- 4. Error Handling
	- 6. Observability
	- 8. Testing
- `docs/architecture/SECURITY_AUTH_PATTERNS.md`
	- 1. Authentication Model
	- 2. Authorization Model
	- 3. Cross-Cutting Security Rules
	- 4. Identity Propagation
	- 8. Domain Constraints

---

## 3. Boundary Analysis

- Layers/services impacted:
	- API adapters for analyst and operations visibility endpoints
	- Inbound ports for ingestion and query use cases
	- Domain/service orchestration for deduplication and ingestion-history handling
	- Outbound ports/adapters for AP email source, accounting source, persistence, and alerting
- Dependency direction:
	- Adapter -> Port -> Service/Domain -> Port -> Adapter
- Cross-layer violations introduced: no (planned)
- Boundary risks identified:
	- Direct API-to-domain coupling bypassing ports
	- Adapter-to-adapter invocation for cross-source deduplication
	- Domain dependence on infrastructure SDK types
- Mitigations:
	- Enforce port-only entry/exit points
	- Keep dedupe policy in domain/service layer
	- Validate dependency rules with boundary enforcement in CI

Compliance with `BOUNDARIES.md`: confirmed for planned design.

---

## 4. API Impact

- API changes required: yes
- Routes affected:
	- Analyst queue read endpoints supporting source filter and timestamp sorting
	- Operations status endpoints for ingestion health/failure visibility
- Versioning impact:
	- New/changed routes must follow repository API versioning conventions
- Request/response structure changes:
	- API responses must use the standard response envelope
	- Request models include source/timestamp filter and sorting parameters
- Error model impact:
	- Domain/service errors mapped to standard API error response shape
- OpenAPI updates required: yes

---

## 5. Security Impact

- Auth pattern used:
	- OAuth2 JWT bearer validation at API adapter boundary
- Authorization enforcement points:
	- Role checks at API entry points for `finance_analyst` and `finance_ops`
- Data classification impact:
	- Invoice content and metadata treated as sensitive business data
- Token handling implications:
	- No token parsing/verification logic outside approved adapter/security components
- Logging/redaction considerations:
	- Structured logs with correlation fields; no secrets or sensitive payload leakage
- Threat considerations:
	- Unauthorized data access, ingestion-source outage misdiagnosis, and sensitive data exposure in logs

---

## 6. Evaluation Impact

From `eval_criteria.yaml`:

- Mode: deterministic
- Criteria affected:
	- Duplicate suppression within same source and across sources
	- Ingestion latency and reliability checks
	- Failure visibility and operational status behavior
- Threshold implications:
	- Must encode NFR thresholds (for example 15-minute ingestion SLA and 99.7% source reliability)
- CI evaluation gate impact:
	- Deterministic criteria are defined and ready for CI evaluation-gate validation

---

## 7. ADR Determination

- ADR required: yes

If yes:
- Proposed title:
	- ADR-001: Invoice Ingestion Source Integration and Deduplication Contract
- Scope:
	- Establish source integration boundaries, dedupe contract, API/security impact, and plan alignment
- Trigger condition (what changed or why required):
	- New/changed integration ports and architectural pattern decisions for multi-source ingestion and deduplication under ADR trigger rules

---

## 8. Preflight Conclusion

- Architecture alignment: compliant
- Security alignment: compliant
- Evaluation alignment: compliant

Final status:
- Approved for planning
