# TS-TIER — Workload Tiering Technical Specification

**Document ID:** TS-TIER-001  
**Version:** `2.0.0`  
**Date:** 2026-08-14
**Parent:** `PRD-DBX-COMPUTE-OPT` v2.0.0; HLA v2.0.0  
**Architecture:** `ARC-CMP-004`  
**Status:** Draft for implementation review  
**Code target:** `src/databricks_compute_optimizer/kernel/tiering/`  

---

# 0. v2.0.0 Architecture Reconciliation

This v2 reconciliation preserves the existing SQL Warehouse business semantics while adopting the Shared Kernel + SQL Warehouse Pack implementation boundary.

- Shared framework/engine code is implemented once under `src/databricks_compute_optimizer/kernel/`.
- SQL Warehouse-specific algorithms, sources, configuration semantics, and providers live under `src/databricks_compute_optimizer/packs/sql_warehouse/`.
- `packs/sql_warehouse/manifest.yaml` points to executable pack capabilities; it is metadata, not duplicate implementation code.
- No future compute pack is implemented by this document.

Tiering is a shared deterministic Kernel service consuming SQLWH Estimator BASELINE output and SQLWH Policy thresholds. It controls **effort/depth**, never Analyzer/Optimizer applicability.

`T1–T4` is distinct from LLM `AR0–AR4`. T-tier may be one AgentReviewRouter input but cannot determine the AR class by itself.

---

# 1. Responsibility

Tiering converts the Estimator's authoritative `BASELINE` annual economic cost for each warehouse into a deterministic T1–T4 priority. It does not query billing data and does not recalculate dollars.

Phase-1 tiering is warehouse-centric. Tiering does not create a multi-warehouse scope object. Beginning Phase 5, O6 still executes whenever it is otherwise applicable; T-tier may only bound topology candidate/search/modeling depth.

---

# 2. Input Contract

```json
{
  "warehouse_id": "WH-123",
  "baseline_cost_estimate_id": "CE-...",
  "annual_economic_cost": 1800000.00,
  "cost_quality": "AUTHORITATIVE",
  "policy_snapshot_id": "PSNAP-..."
}
```

Required input status: Estimator `BASELINE` must be valid. If baseline is blocked, tier is `UNASSIGNED` and downstream optimization is blocked unless Policy explicitly allows diagnostic-only processing.

---

# 3. Phase-1 Algorithm

Default basis: TTM-365 annual economic cost.

```python
def assign_tier(cost, thresholds):
    if cost >= thresholds.T1: return "T1"
    if cost >= thresholds.T2: return "T2"
    if cost >= thresholds.T3: return "T3"
    return "T4"
```

Thresholds are monotonic and policy controlled:

```text
T1_min > T2_min > T3_min >= T4_min = 0
```

No percentile/model/LLM logic is permitted in Phase-1 Tiering.

---

# 4. Output Contract

```json
{
  "contract_version": "1.0.0",
  "tier_result_id": "TIER-...",
  "warehouse_id": "WH-123",
  "tier": "T1",
  "basis": {
    "metric": "TTM_365_ANNUAL_ECONOMIC_COST",
    "value": 1800000.00,
    "currency": "USD",
    "baseline_cost_estimate_id": "CE-..."
  },
  "execution_policy": {
    "beam_width": 5,
    "candidate_budget_profile": "DEEP",
    "statistical_depth": "DEEP",
    "ml_phase2_eligible": true
  },
  "policy_snapshot_id": "PSNAP-..."
}
```

---

# 5. Execution Depth Mapping

Illustrative policy mapping:

| Tier | Deterministic execution | What may vary by tier |
|---|---|---|
| T1 | **all applicable registered Analyzers/Optimizers** | widest bounded candidate domain/beam; deepest statistical modeling; ML may be invoked |
| T2 | **all applicable registered Analyzers/Optimizers** | moderate bounded candidate domain/beam; full required safety modeling; ML may be invoked |
| T3 | **all applicable registered Analyzers/Optimizers** | narrower candidate/beam/modeling budget; statistical fallback/reference retained |
| T4 | **all applicable registered Analyzers/Optimizers** | minimum safe candidate/search budget; no loss of hard evidence/safety checks |

Tier changes compute/search effort, **not capability applicability or financial/runtime correctness**. A tier can never be used as `enabled=false` for an otherwise applicable SQLWH Analyzer/Optimizer.

# 6. Future Evolution

Policy may later add secondary deterministic factors such as:

- opportunity estimate;
- cost growth;
- volatility;
- topology opportunity;
- business criticality.

If introduced, the tier formula must remain explicit and explainable. ML must not silently assign tiers unless a future PRD explicitly changes this authority model. LLM review class AR0–AR4 is assigned separately by AgentReviewRouter.

---

# 7. Errors

| Code | Condition |
|---|---|
| `TIER_BASELINE_BLOCKED` | no authoritative baseline |
| `TIER_POLICY_INVALID` | non-monotonic thresholds |
| `TIER_CURRENCY_MISMATCH` | baseline currency inconsistent with policy |

---

# 8. Tests

- exact threshold boundaries;
- zero cost;
- negative cost rejected;
- same cost/policy -> same tier;
- blocked baseline -> UNASSIGNED;
- tier execution attributes come only from Policy;
- O6 remains a warehouse-ID set inside optimizer logic, not a Tiering scope type.

---

# 9. Component Release Plan

| Release | Scope |
|---|---|
| `REL-TIER-0.1.0` | baseline cost input + T1–T4 thresholds |
| `REL-TIER-0.2.0` | execution-depth mapping + validation |
| `REL-TIER-1.0.0` | Phase-1 complete, integrated with Estimator/Orchestrator |
| `REL-TIER-2.0.0` | optional new deterministic secondary factors / ML invocation eligibility only |

---

# 10. Service Interface

```python
class TieringService(Protocol):
    def assign(
        self,
        baseline: CostEstimate,
        policy: TieringPolicyView,
    ) -> TierResult:
        ...
```

The service is pure and side-effect free. Persistence and scheduling are owned by Runtime/Orchestrator.

---

# 11. Determinism and Ordering

Tier boundaries use exact Decimal comparisons in policy currency. No floating-point rounding is permitted before threshold comparison. If processing multiple warehouses, results are sorted by `(tier_rank, -annual_economic_cost, warehouse_id)` only for presentation/execution ordering; assignment itself is independent of portfolio ordering.

Policy threshold validation occurs before a run:

```text
T1_min > T2_min > T3_min >= 0
```

A threshold edit produces a `PolicyDiff` with Tiering impact; affected warehouses are re-tiered and Orchestrator search depth is recomputed.

---

# 12. Observability

```text
tiering_assignments_total{tier}
tiering_unassigned_total{reason}
tiering_duration_seconds
tiering_annual_cost_usd{tier}
tiering_policy_version
```

Structured logs include `run_id`, `warehouse_id`, baseline estimate ID, cost basis, tier, and policy hash.

---

# 13. Integration Tests

| Test | Assertion |
|---|---|
| `IT-TIER-001` | Estimator BASELINE value maps exactly to configured tier |
| `IT-TIER-002` | threshold policy change reassigns only affected warehouse priorities |
| `IT-TIER-003` | Orchestrator receives exact tier execution-depth view |
| `IT-TIER-004` | blocked financial baseline cannot become T1–T4 authority |
| `IT-TIER-005` | O6 receives tier-derived search budget without tier suppressing O6 applicability |

---

# 14. Phase-1 / Phase-2 Implementation

Phase 1 is pure Python/Decimal and requires no pandas or SQL. Phase 2 retains the same pure assignment function; a Spark/Delta backend may batch-load baseline estimates and persist TierResults, but tier authority remains deterministic and unchanged. ML eligibility in Phase 2 can be a **consequence** of tier (for example deeper ML modeling for T1) but ML does not determine the tier in the approved product.

---

# 15. Definition of Done

- authoritative TTM-365 baseline cost is the Phase-1 input;
- thresholds are monotonic, versioned, and Policy-owned;
- exact boundary behavior is golden-tested;
- TierResult drives search/modeling/candidate depth but cannot suppress an applicable Analyzer/Optimizer or weaken safety/financial correctness;
- warehouse is the sole Phase-1 top-level entity;
- no hidden statistical/ML tier assignment exists.
