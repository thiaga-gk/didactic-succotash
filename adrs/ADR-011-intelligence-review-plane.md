# ADR-011 — Governed Intelligence Review Plane Around the Existing Authoritative Architecture

**Status:** Accepted in v2.0.0 design baseline; included in Gate-6 final review candidate
**Date:** 2026-08-14  
**Parent:** PRD v2.0.0 / HLA v2.0.0  
**Reference design input:** prior hybrid PRD and `TS-LLM-001` v1.1.1, adapted to the SQL Warehouse product decisions  
**Decision scope:** Shared review contracts; SQL Warehouse Phase-3 implementation first

## Context

Deterministic optimization provides reproducibility and financial/configuration authority but can only reason about evidence and relationships represented by its registered capabilities. ML improves prediction but may be uncertain, poorly calibrated, or out-of-domain. LLMs can reason across evidence and challenge assumptions, but they are probabilistic and unsuitable as authoritative configuration or financial decision makers.

The existing SQL Warehouse architecture already has clear owners: Analyzer, Modeler, Optimizer, Estimator, Orchestrator, Decision Engine, Recommendation Package, and Lifecycle Manager. Introducing a second “agent adjudicator” or agent lifecycle would duplicate authority and weaken the architecture.

## Decision

Add an **Intelligence Review Plane around**, not inside, the existing authoritative architecture.

Phase-3 scheduled roles are exactly:

- **Investigator** — tests evidence adequacy and identifies missing/contradictory evidence, risks, ML concerns, and capability gaps.
- **Challenger** — independently attempts to falsify the selected deterministic decision using the original immutable evidence plus the Investigator result.
- **Explainer** — produces a reviewer narrative from authoritative structured values.

A deterministic **AgentReviewRouter** selects AR0–AR4. LLMs do not decide their own invocation.

A deterministic **Review Adapter** validates agent structured outputs and routes legitimate requests to existing authoritative owners. It is not a second Decision Engine.

## Routing taxonomy

Use review-intensity classes rather than reusing workload T1–T4:

```text
AR0 DEEP_CRITICAL
AR1 DEEP_MATERIAL
AR2 DEEP_STANDARD
AR3 EXPLAIN_ONLY
AR4 NO_CHANGE_OR_BLOCKED
```

Routing reasons are separate fields. Default deep-review rule shape:

```text
EXTREME_VALUE
OR (MATERIAL_VALUE AND complexity/risk/conflict/ML-uncertainty/prior-failure)
OR SAFETY_ESCALATION
OR HUMAN_ESCALATION
```

## Phase-3 execution constraints

Phase 3 is:

- packet-only;
- no callable tools;
- no autonomous long-term agent memory;
- bounded immutable evidence packets;
- provider-neutral model client;
- role/value-based model routing;
- strict schema + semantic + evidence validation;
- MLflow tracing/evaluation candidate;
- human production approval preserved.

## Allowed agent request semantics

```text
REQUEST_MORE_EVIDENCE
REQUEST_INPUT_CORRECTION
REQUEST_POLICY_RESOLUTION
REQUEST_STATISTICAL_FALLBACK
REQUEST_BLOCK
ANALYZER_CAPABILITY_GAP
OPTIMIZER_CAPABILITY_GAP
SOURCE_EVIDENCE_GAP
POLICY_GAP
NO_CHANGE
```

Explicitly prohibit:

```text
GENERIC_RERUN
RUN_EXISTING_ANALYZER
RUN_EXISTING_OPTIMIZER
```

because the deterministic workflow executes all applicable registered analyzers/optimizers for the same DecisionContext. The LLM cannot obtain a different deterministic answer by requesting the same work again.

## Review effect

Agent review can lead to:

- no authoritative action;
- evidence collection request;
- source/input correction workflow;
- policy resolution workflow;
- deterministic validation of a statistical-fallback request;
- advisory block request evaluated by existing deterministic Policy/Decision logic;
- durable CapabilityGap.

Authoritative recomputation occurs only after an existing authoritative owner accepts a change that produces a new `authoritative_context_hash`.

## Progressive trust

Initial deep review is shadow/advisory. The deterministic recommendation remains available with orthogonal `agent_review_status`. A later Phase-3 release may make review a reviewer-readiness gate for narrowly selected high-risk classes only after safety/evaluation gates prove value. Deterministic computation remains independent of LLM availability.

## Explanation

Persist `NarrativeExtension` separately from authoritative RecommendationPackage values. Numeric/value echo is deterministically validated; mismatches suppress the narrative. Model/prompt changes alone do not invalidate the authoritative recommendation.

## Alternatives considered

### A. Let agents generate/choose configurations directly
Rejected for reproducibility, auditability, financial integrity, and safety.

### B. Add a new general-purpose deterministic adjudicator component
Rejected because existing Policy/Orchestrator/Decision/Lifecycle components already own those effects; Review Adapter should only validate and route.

### C. Reuse workload T1–T4 for agent routing
Rejected because workload optimization depth and LLM review intensity are different dimensions.

### D. Give Investigator/Challenger general SQL/MCP tools in Phase 3
Rejected for initial release because packet-only review is easier to secure, evaluate, reproduce, and cost-govern. Bounded tools are deferred to Phase 6.

### E. Persistent agent memory
Rejected initially. Governed DecisionContext, validation history, Capability Registry, and outcome records are durable memory; the agent itself remains stateless between reviews.

## Consequences

### Positive
- Adds blind-spot discovery and adversarial review without surrendering deterministic authority.
- LLM outages cannot corrupt deterministic results.
- Capability gaps become durable product-learning inputs.
- Explanation can evolve independently from recommendation truth.
- Same roles can be reused across future compute packs via service-specific evidence payloads.

### Costs
- Requires strict schemas, evidence packet construction, evaluation corpus, model governance, and cost controls.
- Review may add latency/cost for AR0–AR2.
- Progressive-trust gating requires empirical proof, not architectural assumption.

## Guardrails

1. No LLM output directly mutates configuration, cost, savings, confidence, lifecycle, or authoritative context.
2. `REQUEST_BLOCK` is advisory.
3. Same context hash means no authoritative recomputation.
4. Known gaps are referenced/deduplicated rather than rediscovered as new objects.
5. Hidden chain-of-thought is neither stored nor required.
6. Phase-3 tools = none.
7. Explainer authoritative-value mismatch suppresses narrative.
8. Promotion prioritizes missed-risk/unsafe-pass and false-block safety metrics before narrative preference.

## Traceability

- `PRD-FR-PROD-043`, `050`, `053..067`
- `PRD-FR-ARR-*`, `AEP-*`, `INV-*`, `CH-*`, `RA-*`, `EXP-*`, `AIGOV-*`
- `PRD-NFR-PROD-034..042`
- `ARC-AI-LLM-001`, `ARC-FLOW-AGENT-001`, `ARC-CMP-012..015`
