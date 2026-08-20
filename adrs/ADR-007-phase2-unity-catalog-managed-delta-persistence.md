# ADR-007 — Phase-2 Unity Catalog Managed Delta Persistence

**v2.0.0 disposition:** Retained. Phase-2 product-owned managed Delta persistence remains normative; Phase-4 extensions are Deep Diagnostic Intelligence, not a SQL Warehouse Spark-event assumption.

**Status:** Proposed in v1.1.0  
**Date:** 2026-08-13  

## Context

Phase 1 intentionally avoids persisted intermediary Delta tables to maximize time-to-value. Phase 2 requires a durable, scalable data/state layer for DAB/Lakeflow Jobs/PySpark execution, component result lineage, ML governance, lifecycle state, and realized value.

A raw copy of Databricks system tables would duplicate governed source data and create unnecessary storage, freshness, and reconciliation obligations.

## Decision

Phase 2 uses Unity Catalog **managed Delta tables** for product-owned data and state. The normative DDL is `TS-DATA-001`.

Persist:

- run/source/policy manifests;
- normalized external financial inputs such as AWS cost lines and commercial rates;
- canonical warehouse config snapshots needed by product lineage;
- Analyzer, Modeler, Optimizer, Estimator, Tiering, PlanState, and Decision results;
- Recommendation Packages/steps;
- lifecycle current/event history and realized value;
- ML feature/model-evaluation manifests;
- later Phase-4 SQL Warehouse Deep Diagnostic normalized extensions and Phase-5 topology results.

Do **not** persist a raw Bronze duplicate of Databricks system tables by default. PySpark queries system tables directly and persists product-owned normalized/derived results. An explicit future source-contract reason and ADR would be required to change this rule.

Authoritative monetary values use `DECIMAL`, not binary floating-point fields. Issued recommendations and lifecycle events are append-only/immutable; current-state tables use deterministic idempotent merge keys.

## Consequences

- Phase-1 pandas outputs become the canonical parity reference for Phase-2 PySpark/Delta.
- Component contracts remain backend-independent.
- Product lineage survives scheduled/distributed execution.
- Delta schemas become versioned implementation contracts and are golden-tested for round-trip parity.
