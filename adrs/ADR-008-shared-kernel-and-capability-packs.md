# ADR-008 — Shared Optimization Kernel + Compute Capability Packs

**Status:** Accepted in v2.0.0 design baseline; included in Gate-6 final review candidate
**Date:** 2026-08-14  
**Parent:** `PRD-DBX-COMPUTE-OPT` v2.0.0, `HLA-DBX-COMPUTE-OPT` v2.0.0  
**Decision scope:** Product-wide architecture; SQL Warehouse remains the only normative implementation pack

## Context

The SQL Warehouse optimizer has matured into a reusable pattern: deterministic facts and decisions, statistical/ML counterfactuals, authoritative financial estimation, dependency-aware orchestration, lifecycle/realization, and bounded LLM review. The user intends to apply the same architecture to other Databricks compute types.

Copying the SQL Warehouse code/semantics into Job Compute, All-Purpose, Pipelines, or Serverless would create duplicated infrastructure and inconsistent governance. Conversely, forcing all compute types into SQL-specific source fields, A00–A16 meanings, O1–O7 techniques, or one universal telemetry schema would create false abstractions and unsafe recommendations.

## Decision

Adopt:

```text
Databricks Compute Optimization Product
= Shared Optimization Kernel
+ independently governed Compute Capability Packs
```

The Shared Kernel owns reusable contracts/frameworks for:

- Policy resolution/versioning;
- Capability Registry;
- DecisionContext/Evidence Graph;
- Analyzer execution protocol;
- financial Estimator framework;
- workload/value tiering framework;
- statistical/ML Modeler governance/fallback interface;
- Optimizer protocol and immutable internal PlanState semantics;
- Orchestrator dependency/search/selective-reevaluation framework;
- Decision Engine hard-gate/ranking framework;
- AgentReviewRouter and Intelligence Review contracts;
- Recommendation envelope;
- Lifecycle/validation/realized-value framework;
- portfolio aggregation;
- evaluation/golden-test framework.

Each Capability Pack owns compute-specific:

- source adapters/field mappings/retention/fallbacks;
- identity/configuration domain;
- analyzer taxonomy/formulas;
- optimizer techniques/candidate domains;
- statistical/ML features and models;
- financial quantity attribution;
- performance/reliability/security compatibility rules;
- diagnostics;
- application/validation semantics;
- golden fixtures/scenarios.

The SQL Warehouse Capability Pack is the only current normative implementation pack. Future packs are analysis workstreams until their own artifacts are approved.

Cross-pack capability reuse requires explicit applicability and tests. Conceptual similarity does not establish reuse.

Cross-compute optimization/migration is deferred to a separate explicit future capability and cannot be smuggled into an individual pack.

### Implementation rule — Kernel + Pack does not mean duplicate code

The repository implements the Kernel and the active Capability Pack because they perform different responsibilities:

```text
Kernel = reusable engine/contracts
Pack   = compute-specific plug-ins/providers
```

There MUST NOT be two implementations of the same capability/service.

1. A released `(capability_id, semantic_version)` resolves to exactly one executable implementation.
2. SQLWH A00–A16/O1–O7 implementations exist only under `packs/sql_warehouse`.
3. Shared Registry, DecisionContext, Orchestrator, Decision, Lifecycle, and Intelligence Review runtime are implemented once in Kernel.
4. The SQLWH pack supplies provider/profile implementations where a shared Kernel service requires compute-specific behavior; it does not clone the shared service.
5. The SQLWH released capability manifest is `packs/sql_warehouse/manifest.yaml`, co-located with the pack.
6. No parallel `capabilities/sql_warehouse/` implementation tree is permitted.
7. Kernel modules cannot statically import concrete pack implementations; runtime composition resolves them from the released manifest/Registry.
8. Packs cannot import each other.
9. Shared Investigator/Challenger/Explainer runtime is not duplicated by compute type.
10. Architecture tests enforce import boundaries, manifest uniqueness, symbol resolution, and one-capability/one-implementation.


## Alternatives considered

### A. Keep a SQL-Warehouse-only architecture and clone it later
Rejected because shared governance, financial, lifecycle, review, and evaluation semantics would fork and drift.

### B. Build one universal analyzer/optimizer taxonomy for every compute type
Rejected because source telemetry and valid actions differ materially by service. A universal taxonomy would accumulate nullable fields and ambiguous semantics.

### C. Build independent products with no shared kernel
Rejected because it duplicates cross-cutting trust, policy, financial, lifecycle, and AI governance infrastructure.

## Consequences

### Positive
- One product control model across compute types.
- Clear reuse of governance and decision infrastructure.
- SQL-specific semantics stay correct.
- New packs can evolve independently.
- Enables a cross-compute knowledge/capability corpus without premature cross-service optimization.

### Costs / tradeoffs
- Requires explicit kernel/pack interfaces.
- Some apparently similar capabilities may remain duplicated until reuse is proven.
- Repository and documentation hierarchy become more deliberate.

## Guardrails

1. SQLWH A00–A16/O1–O7 are not assumed portable.
2. Future packs require source study → ADR → TSD → release plan → golden tests.
3. Shared Kernel must not become a dumping ground for compute-specific logic.
4. No pack may directly mutate another compute service without separate cross-compute design.
5. Empty placeholder implementations for future packs are discouraged because they imply unsupported scope.

## Traceability

- `PRD-FR-PROD-046`, `070`
- `PRD-FR-PACK-001..004`
- `PRD-NFR-PROD-015`, `044`
- `ARC-PLAT-001`, `ARC-KERNEL-001`, `ARC-PACK-001`

## Review decision

Approval of this ADR approves the reusable platform boundary, **not** implementation scope for any compute pack other than SQL Warehouse.
