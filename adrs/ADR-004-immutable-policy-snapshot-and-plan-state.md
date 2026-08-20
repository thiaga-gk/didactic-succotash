# ADR-004 — Immutable PolicySnapshot and PlanState

**v2.0.0 disposition:** Retained. PlanState remains internal Orchestrator candidate/search state; ADR-010 adds DecisionContext and authoritative context hashing.

**Status:** Proposed with HLA v1.0.0  
**Date:** 2026-08-12

## Context
Policy overrides, optimizer sequencing, and structural candidate branches can otherwise make runs difficult to reproduce or audit.

## Decision
Policy Engine resolves YAML/scoped overrides once per run and issues an immutable PolicySnapshot with schema/version/hash. Portfolio search creates immutable PlanStates linked by parent IDs; optimizers never mutate an existing PlanState.

Policy changes mid-run do not silently alter the active snapshot. PolicyDiff drives later selective invalidation.

## Consequences
- Reproducible and auditable decisions.
- Clear incremental savings lineage.
- Easier debugging and golden testing.
- More persisted metadata, accepted as necessary for trust.
