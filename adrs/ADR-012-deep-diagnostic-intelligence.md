# ADR-012 — Deep Diagnostic Intelligence Uses Compute-Specific Diagnostic Adapters

**Status:** Accepted in v2.0.0 design baseline; included in Gate-6 final review candidate
**Date:** 2026-08-14  
**Parent:** PRD v2.0.0 / HLA v2.0.0  
**Decision scope:** Product-wide diagnostic architecture; SQL Warehouse Phase-4 implementation first

## Context

Earlier SQL Warehouse artifacts labeled Phase 4 “Spark-event enrichment.” That terminology incorrectly implies a universal Spark-event source for SQL Warehouses and would not generalize correctly to other Databricks compute types.

Current Databricks documentation exposes different deep diagnostic surfaces by service. SQL Warehouses have query history and Query Profile/warehouse monitoring surfaces; all-purpose/jobs compute have separate compute/Spark metrics; Lakeflow pipelines have a pipeline event log. Serverless workloads have their own supported query/performance surfaces.

A reusable product therefore needs a common diagnostic contract with compute-specific adapters rather than a universal raw Spark-event dependency.

## Decision

Rename the architecture phase to **Phase 4 — Deep Diagnostic Intelligence**.

Define a Shared-Kernel `DiagnosticEvidence` envelope with pack-specific payloads.

```text
DiagnosticEvidence
├── evidence_id / version
├── resource / execution identity
├── observation timestamp/window
├── source type / source version
├── quality / completeness / permission status
├── normalized deterministic facts
├── bounded artifact refs where approved
└── service_evidence
    ├── SQLWarehouseDiagnosticEvidence
    ├── JobComputeDiagnosticEvidence
    ├── PipelineDiagnosticEvidence
    └── ... future packs
```

For SQL Warehouse Phase 4, validate and use supported SQL-specific execution/profile evidence such as Query Profile/query-execution diagnostics, Query History, warehouse events/monitoring, and performance insights where programmatically available and contractually approved.

Do **not** assume Spark event logs as the SQL Warehouse product source.

For future packs:

- Jobs/All-Purpose may use supported Spark/compute metrics/event-derived evidence;
- Pipelines may use pipeline event logs/query profiles;
- Serverless packs must define only telemetry documented/supported for those services.

Deterministic normalization occurs before Analyzer/Modeler/LLM consumption.

## LLM diagnostic boundary

Phase-4 LLM analysis follows the Phase-3 Intelligence Review authority model:

```text
raw/bounded diagnostic artifact
→ deterministic adapter/normalization
→ governed DiagnosticEvidence
→ Investigator/Challenger review
→ hypothesis/request/gap
→ deterministic validation
```

No direct path exists from raw diagnostic text to configuration or money.

Raw excerpts are exceptional, bounded, redacted, and treated as untrusted data. Structured normalized evidence is preferred.

## Availability/fallback

Deep diagnostics are enrichment unless a future capability explicitly declares them mandatory through Policy/Capability Registry. If unavailable:

- preserve the earlier system-table path;
- lower/qualify confidence or block only according to explicit capability policy;
- never invent unsupported telemetry.

## Alternatives considered

### A. Keep “Spark Events” as the universal phase name
Rejected because it is technically misleading for SQL Warehouses and not portable.

### B. Create a universal raw-event schema
Rejected because services expose fundamentally different execution/diagnostic models.

### C. Give LLM raw logs/profiles directly
Rejected as the default because structured deterministic normalization reduces prompt injection, privacy, context-size, and grounding risk.

## Consequences

### Positive
- Corrects SQL Warehouse telemetry assumptions.
- Makes the architecture reusable across compute types.
- Separates diagnostic transport from normalized evidence semantics.
- Supports deterministic and LLM enrichment with the same authority boundary.

### Costs
- Each pack requires its own source/permission/retention/access analysis.
- SQLWH Phase-4 TSD must verify an actual supported programmatic ingestion path for selected diagnostic evidence.
- Some rich UI diagnostics may not be suitable as automated product inputs and must remain optional/manual evidence.

## Guardrails

1. No pack may claim diagnostic telemetry unsupported by its compute service.
2. Adapter output preserves provenance and quality.
3. Diagnostic schema changes require versioning.
4. Missing optional diagnostics cannot silently become healthy/zero evidence.
5. Raw SQL/log/profile text is minimized and treated as untrusted data.
6. Phase-4 LLM findings remain non-authoritative.

## Traceability

- `PRD-FR-PROD-044`, `068`
- `PRD-NFR-PROD-025`, `039`, `045`
- `ARC-SRC-001`, `ARC-DIAG-001`
