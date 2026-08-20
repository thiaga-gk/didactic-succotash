# Package Manifest — Databricks Compute Optimization Product v2.0.1 Implementation-Ready Patch

**Status:** Final review candidate  
**Normative implementation pack:** SQL Warehouse  
**Implementation-authorized future packs:** none

| Review order | Artifact family | Purpose |
|---:|---|---|
| 1 | `README.md` | implementation boundary, precedence and phase guide |
| 2 | `databricks_compute_optimization_product_prd_v2.0.0.md` | product requirements and hybrid value/control model |
| 3 | `databricks_compute_optimization_high_level_architecture_v2.0.0.md` | reusable Shared Kernel + Capability Pack architecture |
| 4 | `adrs/ADR-001..012` | architectural decisions and v2 dispositions |
| 5 | `tech-specs/TS-CAP-001...` | Shared Kernel Capability Registry |
| 6 | `tech-specs/TS-CTX-001...` | DecisionContext / Evidence Graph / context hash |
| 7 | `tech-specs/00-technical-specification-index.md` | SQLWH technical-spec authority map |
| 8 | `tech-specs/01..12` | SQLWH component/runtime/data TSDs |
| 9 | `tech-specs/TS-LLM-001...` | Phase-3 SQLWH Intelligence Review plane |
| 10 | `tech-specs/14-phase4-deep-diagnostic-intelligence-technical-spec.md` | Phase-4 SQLWH diagnostics |
| 11 | `releases/databricks_sql_warehouse_product_release_plan_v2.0.1.md` | 63-row normative build order |
| 12 | `golden-tests/databricks_sql_warehouse_golden_e2e_test_scenarios_v2.0.1.md` | GT-000..GT-077 |
| 13 | `workstreams/future_compute_capability_pack_workstream_matrix_v2.0.0.md` | future pack analysis requirements |
| 14 | `audits/*` | gate validation reports |

## Excluded intentionally

- no old Phase-3 LLM placeholder TSD;
- no SQL Warehouse Spark-event Phase-4 TSD;
- no duplicate `capabilities/sql_warehouse/` implementation tree;
- no implementation package for future compute types;
- no unrestricted SQL/agent tools in Phase 3.

## Final hardening audit

The `final_audited` package adds:
- `audits/final_scoring_and_data_source_audit_v2.0.0.md`
- `audits/databricks_primary_source_verification_2026-08-14.md`

These supersede earlier DDL-count/source-priority observations where they differ.

## v2.0.1 patch authority

PRD/HLA v2.0.0 remain product/architecture authority. The v2.0.1 downstream implementation patch refines Runtime/Estimator/Data, Release Plan, Golden tests, delivery workflow, and no-CUR financial evidence handling without changing product scope.
