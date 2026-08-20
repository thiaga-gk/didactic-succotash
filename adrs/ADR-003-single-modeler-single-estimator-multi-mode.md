# ADR-003 — One Modeler and One Estimator, Each with Multiple Modes

**v2.0.0 disposition:** Retained. Shared Kernel owns the framework; SQL Warehouse supplies compute-specific model/financial providers.

**Status:** Proposed with HLA v1.0.0  
**Date:** 2026-08-12

## Context
Candidate selection, authoritative planning, forward projection, and realized value all require closely related projection/economic capabilities. Separate components would duplicate logic and create inconsistent semantics.

## Decision
Use one Modeler component for proactive projections, candidate counterfactuals, capacity/runtime simulations, and realization counterfactuals in Phase 1; extend that same component with topology simulation in Phase 5. Use one Estimator component with modes: BASELINE, CANDIDATE, INDEPENDENT, SEQUENCED, AUTHORITATIVE_PLAN, FORWARD, REALIZED, and PROTECTIVE.

The Modeler predicts quantities/outcomes. The Estimator prices quantities. Neither directly chooses the authoritative recommendation.

## Consequences
- One financial truth implementation.
- One projection contract across statistical and ML implementations.
- Candidate and final economics cannot silently diverge in semantics.
