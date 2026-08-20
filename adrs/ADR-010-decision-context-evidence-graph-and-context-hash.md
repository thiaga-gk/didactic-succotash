# ADR-010 — DecisionContext / Evidence Graph + Authoritative Context Hash

**Status:** Accepted in v2.0.0 design baseline; included in Gate-6 final review candidate
**Date:** 2026-08-14  
**Parent:** PRD v2.0.0 / HLA v2.0.0  
**Decision scope:** Shared Optimization Kernel

## Context

The optimizer must be deterministic, support selective reevaluation, explain why a recommendation changed, and prevent agents or operators from triggering pointless reruns. Prior artifacts had immutable PolicySnapshot and PlanState, but no single canonical contract describing the complete authoritative decision inputs or a deterministic test for whether those inputs materially changed.

## Decision

Introduce a versioned **DecisionContext** and logical **Evidence Graph**.

DecisionContext contains or references:

- resource identity;
- source/observation snapshot;
- current effective configuration;
- relevant PolicySnapshot/version/hash;
- applicable RegisteredCapability set and versions;
- deterministic Analyzer results;
- admitted statistical/ML prediction refs and versions;
- authoritative financial basis;
- candidate domain/dependency version;
- material prior validation/realization state where applicable;
- source/component/version lineage.

Compute a deterministic `authoritative_context_hash` from canonical authoritative inputs.

LLM outputs, agent prose, NarrativeExtension, hidden reasoning, and unvalidated agent requests are excluded.

Binding rule:

```text
if new_authoritative_context_hash == previous_authoritative_context_hash:
    do not perform authoritative recomputation
```

A separate `agent_review_fingerprint` may incorporate review-relevant model/prompt/schema/router versions without invalidating the authoritative recommendation.

## Evidence Graph

Evidence Graph is a logical lineage:

```text
source evidence
→ deterministic fact
→ policy / prediction
→ candidate / PlanState
→ DecisionResult
→ AgentReviewRecord
→ validation
→ realized value
→ capability gap / evaluation corpus
```

No graph database is required by this ADR.

## Valid context-changing events

Examples include:

- new material source evidence;
- validated source/input correction;
- effective configuration/workload/regime change;
- price/financial basis change;
- policy resolution affecting decision domain;
- approved statistical fallback replacing a challenged ML signal;
- material validation/realized outcome change;
- new released applicable capability.

An LLM request alone is not a valid context-changing event.

## Alternatives considered

### A. Use run ID as the rerun identity
Rejected because a new run can contain identical authoritative inputs.

### B. Hash only source snapshot/config
Rejected because policy, capability versions, admitted model outputs, and financial basis can change decisions.

### C. Include LLM findings in the authoritative hash
Rejected because probabilistic text would become authoritative decision state without independent validation.

### D. Always rerun the full pipeline weekly
Rejected as the only mechanism because it wastes compute and does not explain causal invalidation; weekly refresh may still occur as a scheduled policy action while reuse remains dependency-safe.

## Consequences

### Positive
- Precise determinism/replay contract.
- Clean separation between authoritative state and AI review state.
- Enables dependency-directed selective reevaluation.
- Makes “same context → same answer” machine-testable.
- Provides durable evidence lineage.

### Costs
- Context canonicalization/hashing must be carefully specified and golden-tested.
- Every material dependency must declare its hash contribution.
- Schema evolution requires migration/versioning rules.

## Guardrails

1. Hash inputs are typed and versioned.
2. Unknown material context fields cannot silently default to favorable values.
3. LLM findings remain outside authoritative context until existing authoritative owners validate supporting evidence/policy/capability changes.
4. Golden mutation tests prove that each material decision input changes the hash when expected.
5. Context hash equality suppresses recomputation; it does not suppress a non-authoritative narrative refresh when review fingerprint policy says otherwise.

## Traceability

- `PRD-FR-PROD-051..052`, `058`, `060`, `062`, `064`
- `PRD-FR-CTX-001..006`
- `PRD-NFR-PROD-001..003`, `008`, `033`, `040`
- `ARC-DCTX-001`, `ARC-EXEC-001`
