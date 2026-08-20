# ADR-002 — Deterministic Authority with Statistical Phase-1 and ML Phase-2 Projection

**v2.0.0 disposition:** Retained and extended by ADR-011. Deterministic authority remains binding; LLMs add review/explanation only.

**Status:** Proposed with HLA v1.0.0  
**Date:** 2026-08-12

## Context
Recommendations must be reproducible and safe, while future demand, runtime and counterfactual behavior require projection.

## Decision
Observed facts come from deterministic Analyzers. Phase-1 statistical models and Phase-2 ML models operate only through the Modeler contract and return projections/uncertainty. Deterministic Optimizers apply Policy and hard guardrails to those projections and issue the authoritative technique decision. Decision Engine applies deterministic plan selection rules.

ML is admitted only by Policy and must retain statistical fallback.

## Consequences
- Prediction can evolve without changing authoritative decision ownership.
- ML failure/OOD can fall back to statistical methods.
- Same input/Policy/component versions preserve deterministic config decisions where model determinism requirements are met.
