# ADR-009 — Capability Registry from Phase 1 + Governed Capability-Gap Lifecycle

**Status:** Accepted in v2.0.0 design baseline; included in Gate-6 final review candidate
**Date:** 2026-08-14  
**Parent:** PRD v2.0.0 / HLA v2.0.0  
**Decision scope:** Shared Optimization Kernel

## Context

The deterministic runtime must know exactly which analyzers, optimizers, modeling/evidence capabilities and versions are approved and applicable. Phase-3 LLM review can also discover material conditions that the current deterministic product does not represent.

Relying on probabilistic agents to rediscover the same unknown every week would be wasteful and unsafe. Allowing an LLM-created database row to become executable would violate release governance.

## Decision

Create a first-class **Capability Registry** in the Shared Kernel from Phase 1.

The Registry has two distinct semantic families:

```text
REGISTERED_CAPABILITY      # executable only when released/source-controlled
CAPABILITY_GAP             # durable, non-executable missing capability
```

Executable capability authority is established by source-controlled, reviewed, tested, released code/manifests. The operational Registry records capability metadata, service applicability, version, dependencies, status, digests, and release provenance, but a mutable runtime row cannot create executable code.

Beginning Phase 3, the Registry additionally persists gaps of type:

```text
ANALYZER
OPTIMIZER
SOURCE_EVIDENCE
POLICY
```

Gap lifecycle:

```text
DISCOVERED
→ VALIDATED
→ TRIAGED
→ APPROVED_FOR_DESIGN
→ IMPLEMENTED / RESOLVED
→ VALIDATED
→ RELEASED / APPROVED
→ CLOSED with resolution_ref
```

with `DEFERRED` and `REJECTED` branches. Analyzer/optimizer/source-evidence gaps can resolve to a released `RegisteredCapability`; policy gaps resolve to an approved versioned Policy artifact. They are not forced into the same executable type.

## Deterministic duplicate handling

A gap uses a structured signature based on semantic fields such as compute type, gap type, decision domain, missing-capability semantic, and affected registered capability IDs. Agent prose is not the deduplication key.

Subsequent equivalent observations:

- reference the existing `gap_id`;
- append materially new evidence;
- update occurrence/resource counts;
- update severity/value-at-risk when deterministically recomputable;
- do not create duplicate executable semantics.

Known open gaps are included in future relevant review packets. Routing/review-reuse policy may suppress redundant deep review when no new context exists.

## Impact of closing a gap

A gap does not alter the current deterministic algorithm at discovery time. After an analyzer/optimizer/source capability is designed, implemented, golden-tested, released, and registered, or after a material policy gap is resolved through an approved Policy version:

```text
applicable capability/policy state changes
→ registry/policy/context version changes
→ authoritative_context_hash changes
→ dependency-directed authoritative reevaluation
```

The reevaluation occurs because the authoritative context changed, not because the LLM requested a different answer.

## Alternatives considered

### A. Separate “gap backlog” unrelated to runtime capability inventory
Rejected because closing a gap must link deterministically to the capability/version that resolves it.

### B. Let the LLM create new analyzers/optimizers dynamically
Rejected because this bypasses deterministic design, review, testing, and release governance.

### C. Rely on prompt memory to remember known gaps
Rejected because prompt/model memory is probabilistic, difficult to audit, and can become stale or poisoned.

## Consequences

### Positive
- Durable organizational memory independent of LLM behavior.
- Converts repeated unknowns into deterministic product IP.
- Supports recurrence/materiality prioritization.
- Prevents duplicate agent work and duplicate gap records.
- Creates explicit lineage from discovered problem to released capability.

### Costs
- Requires registry schema, lifecycle, governance workflow, and source-control manifests.
- Requires deterministic semantic signatures and merge rules.
- Adds triage/product-management responsibility.

## Guardrails

1. `CAPABILITY_GAP` is never executable.
2. Operational registry mutation alone cannot authorize execution.
3. Only released/source-controlled `RegisteredCapability` versions may execute.
4. New capabilities require golden tests before registration.
5. Gaps are scoped by compute type/applicability; a SQLWH gap does not automatically become a Job Compute capability.

## Traceability

- `PRD-FR-PROD-047..049`, `061..062`
- `PRD-FR-CAP-001..009`
- `PRD-NFR-PROD-031..032`
- `ARC-CMP-011`, `ARC-CAP-001`
