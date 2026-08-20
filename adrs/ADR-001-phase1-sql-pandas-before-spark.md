# ADR-001 — Phase-1 SQL Warehouse + pandas Before PySpark/Delta Scale-Out

**v2.0.0 disposition:** Retained for SQL Warehouse. Phase 1 remains SQL Warehouse + bounded pandas/Arrow; Phase 2 remains the scale-out boundary.

**Status:** Proposed with HLA v1.0.0  
**Date:** 2026-08-12

## Context
The product needs rapid end-to-end value validation while component contracts and deterministic logic are still evolving. Building distributed Spark/Delta infrastructure first would lengthen the feedback loop and create migration coupling before the algorithms are proven.

## Decision
Implement all Phase-1 logical components using SQL pushdown through an existing Databricks SQL warehouse and bounded Python/pandas/Arrow processing. Do not require persisted intermediary Delta tables. Persist only compact run/lifecycle/lineage artifacts through a repository abstraction.

After all Phase-1 component releases and golden E2E gates pass, introduce Declarative Automation Bundles, Lakeflow Jobs classic job compute, PySpark, Unity Catalog Delta persistence, and governed ML as Phase 2. Statistical modeling remains the fallback/reference implementation. Require pandas↔PySpark output parity before promotion. This is a project-specific target-compute decision; Databricks currently supports and often recommends serverless compute for supported job tasks, so the choice of classic jobs compute MUST be revalidated at the Phase-2 gate without changing the approved requirement unless an ADR supersedes it.

## Consequences
- Faster component iteration and value proof.
- SQL must perform heavy filtering/aggregation to keep pandas bounded.
- Phase-1 persistence is intentionally lightweight.
- Runtime/repository interfaces must isolate migration points.
- The SQL Connector is not reused as the jobs-compute execution mechanism; Phase 2 uses native PySpark.
