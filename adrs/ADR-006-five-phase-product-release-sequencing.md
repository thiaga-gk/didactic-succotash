# ADR-006 — Five-Phase Product Release Sequencing

**v2.0.0 disposition:** PARTIALLY SUPERSEDED. The old five-phase sequence is NOT implementation authority in v2.0.0. The retained decision is that A15/M06/O6 topology is deferred to Phase 5. The active sequence is the six-phase PRD/HLA and `releases/databricks_sql_warehouse_product_release_plan_v2.0.1.md`.

**Status:** Superseded for product sequencing in v2.0.0; topology-deferral decision retained  
**Date:** 2026-08-13  

## Historical Context — do not use as the active v2 release sequence

The product needs an implementation order that proves trustworthy single-warehouse savings quickly before introducing distributed persistence, ML, LLMs, Spark-event enrichment, and multi-warehouse topology. Earlier artifacts allowed A15/M06/O6 topology in Phase 1, which conflicts with the approved implementation sequence.

## Historical Decision — superseded except for Phase-5 topology deferral

Adopt the following normative phases:

| Phase | Capability boundary |
|---:|---|
| 1 | Repository/connectivity foundations; SQL Warehouse + bounded Arrow/pandas local runtime; deterministic analyzers/optimizers; statistical M01–M05/M07/M08; O1–O5 and O7; single-warehouse only. |
| 2 | Declarative Automation Bundles + Lakeflow Jobs classic jobs compute + PySpark + Unity Catalog managed Delta; pandas↔PySpark parity; governed ML behind the Modeler contract with mandatory statistical fallback. |
| 3 | LLM integration placeholder only until a separately approved PRD/HLA/TS/GT addendum defines roles, contracts, prompts, tools, memory, authority, cost controls, and evaluation. |
| 4 | Spark-event ingestion and deterministic analyzer enrichment; LLM Spark-event analysis only if the Phase-3 LLM design has been approved. |
| 5 | A15 + M06 + O6 warehouse split/merge topology; O6 precedes and invalidates downstream O1→O5→O2→O4→O3 optimization for target warehouses. |

The top-level product entity remains `WAREHOUSE` in every phase. O6 carries multi-warehouse IDs and internal workload placements inside its own Phase-5 contract.

The product-level release-plan table is the normative implementation order. Component `REL-*` plans must map to it.

## Consequences

- Phase 1 can prove end-to-end value without Delta, ML, LLM, Spark events, or topology.
- Phase 2 is an execution/persistence migration plus ML admission, not a rewrite of deterministic domain authority.
- A15/M06/O6 cannot block Phase-1 release readiness.
- Phase-5 topology must re-use the mature single-warehouse pipeline rather than duplicating it.
- Golden scenarios are phase-labelled; topology scenarios are Phase 5.
