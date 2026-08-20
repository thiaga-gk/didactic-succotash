# Databricks Compute Optimization Product — v2.0.0 Final Review Candidate

This package is the reconciled product/design baseline for a reusable **Databricks Compute Optimization Product** with **SQL Warehouse as the only implementation-authorized Capability Pack** in v2.0.0.

## Implementation model — read this first

Implement **both** the Shared Kernel and the SQL Warehouse Pack because they have different responsibilities. **Do not implement the same capability twice.**

```text
Shared Kernel
= reusable engines/contracts implemented once

SQL Warehouse Pack
= SQLWH-specific analyzers, optimizers, model implementations,
  source adapters, diagnostics and provider/profile extensions

packs/sql_warehouse/manifest.yaml
= metadata that points to the SQLWH executable implementations;
  it is not another implementation tree
```

Binding rule:

> A released `(capability_id, semantic_version)` resolves to exactly one executable implementation.

Examples:
- Kernel owns Capability Registry mechanics; SQLWH pack owns A00–A16 implementations.
- Kernel owns DecisionContext hashing; SQLWH pack contributes typed SQLWH context fields.
- Kernel owns Orchestrator/Decision/Lifecycle frameworks; SQLWH pack provides compute-specific providers where required.
- Kernel owns shared Investigator/Challenger/Explainer runtime; SQLWH pack contributes its evidence projection/profile.
- Kernel MUST NOT statically import concrete SQLWH implementations.
- Packs MUST NOT import/call other packs.

## Authoritative document precedence

If wording conflicts, stop implementation and resolve the conflict using this precedence:

1. `databricks_compute_optimization_product_prd_v2.0.0.md`
2. `databricks_compute_optimization_high_level_architecture_v2.0.0.md`
3. accepted ADRs and v2 dispositions
4. `tech-specs/*`
5. `releases/databricks_sql_warehouse_product_release_plan_v2.0.1.md`
6. `golden-tests/databricks_sql_warehouse_golden_e2e_test_scenarios_v2.0.1.md`

Golden tests validate upstream requirements; they do not silently redefine them.

## ADR-006 warning

`ADR-006-five-phase-product-release-sequencing.md` is retained for historical lineage only.

- Its **five-phase sequence is superseded**.
- Its decision to defer **A15/M06/O6 topology to Phase 5 is retained**.
- The active release sequence is the six-phase PRD/HLA and v2 SQL Warehouse Product Release Plan.

## Six phases

| Phase | SQL Warehouse outcome |
|---:|---|
| 1 | Shared-Kernel foundation + SQLWH/pandas deterministic/statistical product; current cost/savings/value proof |
| 2 | DAB + Lakeflow Jobs + PySpark + managed Delta + governed ML with mandatory statistical fallback |
| 3 | Packet-only Intelligence Review: AR0–AR4, Investigator, Challenger, Explainer, Review Adapter; **zero callable tools** |
| 4 | SQL Warehouse **Deep Diagnostic Intelligence** using validated SQLWH diagnostic sources; no universal Spark-event assumption |
| 5 | A15 + M06 + O6 topology split/merge, then downstream O1→O5→O2→O4→O3 reevaluation |
| 6 | Separately gated read-only Portfolio Copilot + bounded typed tools; detailed Phase-6 TSD/security/evaluation approval required before production |

## Deterministic authority

- Every phase/applicability-valid registered Analyzer and Optimizer executes.
- T1–T4 changes bounded candidate/search/model/ML depth; it does not suppress an applicable Analyzer/Optimizer.
- ML predicts; it does not choose authoritative configuration or money.
- LLM investigates, challenges and explains; it does not choose authoritative configuration or money.
- An LLM cannot request an existing Analyzer/Optimizer to rerun against the same DecisionContext.
- Same `authoritative_context_hash` means no authoritative recomputation.
- Capability gaps are durable, deduplicated and non-executable until normal design/test/release.
- Production changes remain HITL unless a separately approved future release changes that policy.

## Future compute packs

Job Compute, All-Purpose Compute, Lakeflow Pipelines, Serverless Jobs/Notebooks and cross-compute migration are **analysis workstreams only** in this package.

Do not create empty production packs or infer SQL Warehouse rules for them. Each requires its own source/platform study, ADRs, TSDs, release plan and Golden E2E suite before implementation authority.

See `workstreams/future_compute_capability_pack_workstream_matrix_v2.0.0.md`.

## Review gates

- Gate 4: component/runtime/data/diagnostic reconciliation — PASS
- Gate 5: Product Release Plan + Golden E2E — PASS
- Gate 6: final package audit — see `audits/gate6_final_package_audit_report_v2.0.0.md`

## v2.0.1 implementation hardening

This package retains PRD/HLA v2.0.0 product scope and adds patch-level implementation controls:

- one Git worktree/`release/<release-id>` branch per Product Release from synchronized `develop`;
- merge into `develop` only after real source-system E2E on the exact final commit;
- source-controlled AWS price-registry planning fallback while CUR/Data Exports are unavailable;
- 50-table Phase-2/later-extension Delta DDL including Bronze price-registry snapshot;
- Golden `GT-077` for no-CUR financial integrity;
- explicit Control + Bronze → Silver → Gold + ML medallion semantics.
# didactic-succotash
