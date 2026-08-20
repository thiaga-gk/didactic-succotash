# TS-POL — Policy Engine Technical Specification

**Document ID:** TS-POL-001  
**Version:** `2.0.0`
**Date:** 2026-08-14  
**Parent PRD:** `databricks_compute_optimization_product_prd_v2.0.0.md`  
**Parent HLA:** `databricks_compute_optimization_high_level_architecture_v2.0.0.md`  
**Parent requirements:** `PRD-FR-POL-001..012`, `PRD-NFR-POL-001..003`  
**Architecture:** `ARC-CMP-001`, `ARC-CMP-001`, `ARC-PLAT-002`  
**Status:** Draft for implementation review  
**Code target:** `src/databricks_compute_optimizer/kernel/policy/ + packs/sql_warehouse/policy/`  

---

# 0. v2.0.0 Architecture Reconciliation

This v2 reconciliation preserves the existing SQL Warehouse business semantics while adopting the Shared Kernel + SQL Warehouse Pack implementation boundary.

- Shared framework/engine code is implemented once under `src/databricks_compute_optimizer/kernel/`.
- SQL Warehouse-specific algorithms, sources, configuration semantics, and providers live under `src/databricks_compute_optimizer/packs/sql_warehouse/`.
- `packs/sql_warehouse/manifest.yaml` points to executable pack capabilities; it is metadata, not duplicate implementation code.
- No future compute pack is implemented by this document.

The Policy Engine itself is a single Kernel service. The SQLWH pack supplies schema extensions/default profiles only; it does not implement a second Policy Engine.

New v2 Policy domains include `agent_review.*`, Capability Registry compatibility, DecisionContext decision-vs-rendering policy projections, and Phase-4 diagnostic feature gates. T1–T4 policy MUST NOT disable an otherwise applicable registered SQLWH Analyzer/Optimizer.

---

# 1. Responsibility

The Policy Engine is the deterministic rules authority. It validates versioned YAML, resolves scoped overrides, applies non-relaxable enterprise hard guardrails, emits an immutable `PolicySnapshot`, and calculates `PolicyDiff` for selective invalidation.

It MUST NOT calculate telemetry, predictions, optimization candidates, financial values, recommendation results, or lifecycle state.

---

# 2. Inputs and Outputs

## 2.1 Inputs

```python
PolicyResolveRequest(
    environment: str,
    workspace_id: str,
    warehouse_id: str,
    warehouse_type: str,
    cost_tier: str | None,
    workload_criticality: str | None,
    run_overrides: dict | None,
    policy_bundle_version: str | None,
)
```

Inputs are runtime context only. `WAREHOUSE` is the product optimization entity; there is no `WORKLOAD_GROUP` or `TOPOLOGY_GROUP` policy scope type. **O6 is dormant before Phase 5.** Beginning in Phase 5, O6 uses policy views resolved for each participating warehouse plus topology-specific policy keys.

## 2.2 Outputs

- `PolicySnapshot`
- component-specific policy views
- `PolicyDiff(old, new)`
- validation errors/warnings

---

# 3. Configuration Layout

```text
config/policy/
├── schema.yaml
├── defaults.yaml
├── enterprise_guardrails.yaml
├── environments/
│   ├── dev.yaml
│   ├── test.yaml
│   └── prod.yaml
├── workspaces/
│   └── <workspace-id>.yaml
├── warehouses/
│   └── <warehouse-id>.yaml
└── examples/
```

Enterprise guardrails SHOULD be protected by repository permissions and deployment controls separate from normal workspace overrides.

---

# 4. Deterministic Precedence

Resolution order from lowest to highest override priority:

```text
Global defaults
→ Environment
→ Workspace
→ Warehouse type
→ Cost tier
→ Workload criticality
→ Warehouse-specific override
→ Governed run override
```

`enterprise_guardrails` are not an override layer. They are post-resolution constraints that cannot be weakened.

## TS-POL-RES-001 — resolution algorithm

```python
def resolve_policy(bundle, context):
    validate_schema(bundle)
    layers = [
        bundle.defaults,
        bundle.environments.get(context.environment),
        bundle.workspaces.get(context.workspace_id),
        bundle.warehouse_types.get(context.warehouse_type),
        bundle.tiers.get(context.cost_tier),
        bundle.criticality.get(context.workload_criticality),
        bundle.warehouses.get(context.warehouse_id),
        context.run_overrides,
    ]
    resolved = deep_merge_in_fixed_order(layers)
    enforce_enterprise_guardrails(resolved, bundle.enterprise_guardrails)
    semantic_validate(resolved)
    canonical = canonicalize(resolved)
    return immutable_snapshot(canonical, sha256(canonical))
```

Rules:

- map merge is recursive;
- scalar/list values replace the lower layer unless the schema explicitly declares `merge_strategy`;
- unspecified values inherit;
- unknown keys fail validation by default;
- YAML anchors are allowed only if the parsed canonical data remains schema-valid;
- environment-dependent interpolation is prohibited inside authoritative policy values except explicitly whitelisted secret/reference fields.

---

# 5. Hard Guardrails

Guardrail examples:

```yaml
enterprise_guardrails:
  performance:
    absolute_max_p95_runtime_regression_pct: 5
  security:
    require_security_eligibility_pass: true
  financial:
    authoritative_currency: USD
  experimental_features:
    allow_unapproved_preview: false
```

A downstream override can tighten a guardrail but cannot loosen it.

Example:

```text
hard ceiling = +5% P95 runtime
workspace override = +2%    → valid
workspace override = +10%   → POLICY_HARD_GUARDRAIL_VIOLATION
```

---

# 6. Canonical Policy Schema

The following is the minimum Phase-1 schema. Exact numeric defaults remain configuration, not source-code constants.

```yaml
policy_schema_version: "1.0.0"
policy_version: "1.0.0"

analysis:
  windows_days: [7, 30, 90, 365]
  percentiles: [50, 95, 99]
  decision_percentile: 95
  risk_percentile: 99
  min_query_count: 30
  source_query_max_days_per_batch: 31
  timezone: UTC

data_quality:
  min_query_coverage_pct: 95
  min_billing_coverage_pct: 99
  min_config_coverage_pct: 100
  max_source_age_hours: 24
  min_aws_attribution_pct: 95

performance:
  max_p95_runtime_regression_pct: 5
  normalize_by_workload_class: true
  normalize_by_volume: true

reliability:
  max_failure_rate_regression_pct: 0
  max_retry_rate_regression_pct: 0

capacity:
  decision_percentile: 95
  risk_percentile: 99
  headroom_pct: 20

modeler:
  implementation: statistical
  forward_horizon_days: 365
  interval_pct: 95
  fixed_seed: 1701
  allow_out_of_domain: false
  fallback_to_statistical: true

orchestrator:
  standalone_enabled: true
  portfolio_enabled: true
  optimizer_order: [O6, O1, O5, O2, O4, O3]
  protective_optimizers: [O7]
  beam_width: {T1: 5, T2: 3, T3: 2, T4: 1}
  max_candidates_per_optimizer: 50
  dominance_pruning: true
  branch_and_bound: true

optimizers:
  O1: {enabled: true}
  O2: {enabled: true, atomic_bundle: true}
  O3: {enabled: true}
  O4: {enabled: true}
  O5: {enabled: true}
  O6: {enabled: true}
  O7: {enabled: false}

features:
  allow_preview_targets: false
  allow_beta_targets: false
  lakehouse_realtime: false
  warehouse_statement_timeout: false
  warehouse_5x_large: false

agent_review:
  enabled: false                       # activates in Phase 3 release
  progressive_trust_mode: SHADOW
  extreme_value_threshold_usd: null    # calibrated Policy value
  material_value_threshold_usd: null
  deep_review:
    ambiguity: true
    conflicting_evidence: true
    elevated_risk: true
    ml_uncertainty: true
    prior_failure: true
  manual_escalation_enabled: true
  safety_escalation_enabled: true
  budgets:
    per_review_usd: null
    weekly_portfolio_usd: null
  tools_enabled: false                 # MUST remain false in Phase 3

diagnostics:
  phase4_enabled: false
  query_profile_ingestion_enabled: false  # require validated acquisition contract

estimator:
  annual_window_days: 365
  currency: USD
  databricks_rate_priority: [contract, invoice_effective, system_list]
  aws:
    economic_basis: net_effective
    calculate_cash_realizable: true
    calculate_commitment_freed: true
  internal_decimal_scale: 8

decision:
  primary_objective: annual_economic_savings
  near_equivalent_savings_pct: 5
  tie_break_order: [lower_risk, higher_confidence, lower_effort, lower_disruption]

recommendation:
  max_material_alternatives: 2
  minimum_alternative_savings_ratio: 0.75
  labels: {}

lifecycle:
  full_refresh_cadence: weekly
  validation_min_days: 7
  validation_min_queries: 100
  require_representative_regime: true
  suppress_equivalent_recommendations: true
  material_savings_delta_pct: 5
```

The schema validator MUST reject accidental YAML key ` decision` (leading whitespace) or any unknown key after parsing; the example above is illustrative and implementation files MUST use exact canonical keys.

---

# 7. PolicySnapshot Contract

```json
{
  "contract_version": "1.0.0",
  "policy_snapshot_id": "PSNAP-...",
  "schema_version": "1.0.0",
  "policy_version": "1.3.0",
  "policy_hash": "sha256:...",
  "resolved_at_utc": "...",
  "context": {
    "environment": "prod",
    "workspace_id": "WS1",
    "warehouse_id": "WH1",
    "warehouse_type": "PRO",
    "cost_tier": "T1",
    "workload_criticality": "HIGH"
  },
  "applied_layers": ["defaults", "prod", "workspace:WS1", "type:PRO", "tier:T1"],
  "resolved": {},
  "override_audit": [],
  "validation": {"status": "VALID", "warnings": []}
}
```

The resolved map is immutable for the duration of an authoritative run.

---

# 8. Component Policy Views

`PolicySnapshot` may be projected into typed views:

```python
AnalyzerPolicyView
TieringPolicyView
ModelerPolicyView
OptimizerPolicyView
EstimatorPolicyView
DecisionPolicyView
RecommendationPolicyView
LifecyclePolicyView
CapabilityRegistryPolicyView
AgentReviewPolicyView
DiagnosticPolicyView
```

Views MUST retain `policy_snapshot_id` and `policy_hash` and MUST NOT mutate values.

---

# 9. PolicyDiff

`PolicyDiff` compares canonical resolved snapshots and maps changed JSON paths to invalidation domains.

Example:

```json
{
  "old_policy_hash": "...",
  "new_policy_hash": "...",
  "changes": [
    {
      "path": "capacity.headroom_pct",
      "old": 20,
      "new": 30,
      "impact": ["O2", "O3", "O4", "ESTIMATOR", "RECOMMENDATION"]
    }
  ]
}
```

Minimum dependency map:

| Policy key family | Invalidate |
|---|---|
| `analysis.*` | affected Analyzer → Modeler → Optimizer → Estimator → Decision → Recommendation |
| `data_quality.*` | A00 and consumers of newly blocked/unblocked evidence |
| `performance.*` | affected Optimizers + Decision; Modeler outputs may be reused if inputs unchanged |
| `capacity.*` | O2 and downstream dependent O3/O4 evaluation |
| `modeler.*` | Modeler and all optimizer branches consuming changed projections |
| `orchestrator.*` | next search/orchestration; evidence need not be recalculated |
| `optimizers.Ox.*` | optimizer `Ox` and dependency-directed downstream paths |
| `estimator.*` | Estimator + Decision + Recommendation |
| `decision.*` | Decision + Recommendation only unless new hard gates require candidate revalidation |
| `recommendation.labels.*` | Recommendation rendering only |
| `lifecycle.*` | Lifecycle only unless it triggers new validation/reoptimization |
| `features.*` | optimizer(s) touching the gated feature plus downstream plan selection |
| `agent_review.*` | AgentReviewRouter / Evidence Packet / review execution only; no authoritative recompute unless the changed field is also an authoritative decision policy |
| `diagnostics.*` | Phase-4 diagnostic adapter/enrichment and consumers |
| `capability_registry.*` | Registry snapshot/applicability validation; changed released applicable capability may create new DecisionContext |

---

# 10. Semantic Validation Rules

Examples:

- `decision_percentile` must be in `analysis.percentiles`.
- `risk_percentile >= decision_percentile`.
- `min_query_count > 0`.
- `beam_width` values are positive integers.
- T1–T4 execution-depth policy cannot disable an otherwise applicable registered Analyzer or Optimizer.
- Phase-3 `agent_review.tools_enabled` must be `false`.
- LLM `AR0–AR4` review classes are not aliases for workload `T1–T4`.
- optimizer order contains each enabled portfolio optimizer at most once.
- `O7` cannot be included in the normal performance-preserving portfolio sequence.
- production Preview/Beta target cannot be enabled if enterprise guardrail forbids it.
- `max_p95_runtime_regression_pct` cannot exceed enterprise ceiling.
- `internal_decimal_scale` must be >= 8 for authoritative monetary calculations; output currency rounding is owned by Estimator policy.
- `minimum_alternative_savings_ratio` must be in `[0,1]`.

---

# 11. Error Semantics

| Code | Condition | Behavior |
|---|---|---|
| `POLICY_SCHEMA_INVALID` | YAML/schema failure | fail run |
| `POLICY_UNKNOWN_KEY` | unknown key | fail run |
| `POLICY_SEMANTIC_CONFLICT` | internally inconsistent settings | fail run |
| `POLICY_HARD_GUARDRAIL_VIOLATION` | override weakens enterprise rule | fail run |
| `POLICY_VERSION_INCOMPATIBLE` | unsupported schema/component compatibility | fail run |
| `POLICY_CONTEXT_INCOMPLETE` | required workspace/warehouse context missing | fail warehouse evaluation |

---

# 12. Observability

Emit:

- `policy.resolve.count`
- `policy.resolve.duration_ms`
- `policy.validation.failure_count`
- `policy.diff.changed_key_count`
- `policy.snapshot.hash`
- applied-layer list in structured logs
- rejected override path/reason without secrets

Never log policy fields classified as secrets.

---

# 13. Tests

Required unit/contract cases:

1. deterministic resolution with identical inputs;
2. every precedence boundary;
3. hard guardrail tightening allowed / loosening rejected;
4. unknown key rejection;
5. semantic conflict rejection;
6. canonical hash stable across YAML ordering/comments;
7. `PolicyDiff` impact map for each policy family;
8. mid-run policy file mutation cannot change existing snapshot;
9. warehouse-only Phase-1 context; O6 remains dormant until Phase 5 and never creates a new top-level policy scope;
10. component policy views preserve parent hash.

---

# 14. Component Release Plan

| Release | Phase | Scope | Exit criteria |
|---|---:|---|---|
| `REL-POL-0.1.0` | 1 | YAML schema + loader + canonicalization | schema tests; stable hash |
| `REL-POL-0.2.0` | 1 | deterministic resolver + hard guardrails | precedence/guardrail golden unit tests |
| `REL-POL-0.3.0` | 1 | typed PolicySnapshot/views | all component mocks consume snapshot |
| `REL-POL-0.4.0` | 1 | PolicyDiff + invalidation mapping | selective-impact contract tests |
| `REL-POL-1.0.0` | 1 | Phase-1 production-ready policy engine | compatibility, observability, full contract suite |
| `REL-POL-2.0.0` | 2 | ML admission/fallback and Phase-2 runtime policy extensions | no Phase-1 schema break; migration tested |
| `REL-POL-2.1.0` | 2 | ML champion/challenger admission thresholds, calibration/OOD/drift and fallback policy hardening | ML governance Golden tests pass; statistical fallback remains mandatory |
| `REL-POL-3.0.0` | 3 | AR0–AR4 routing, progressive-trust, agent budgets, Phase-3 `tools_enabled=false` | routing/budget/authority golden tests pass |
| `REL-POL-4.0.0` | 4 | SQLWH Deep Diagnostic feature/source gates | diagnostic policy/fallback tests pass |
| `REL-POL-5.0.0` | 5 | A15/M06/O6 topology policy extensions | Phase-5 topology policy tests pass |
| `REL-POL-6.0.0` | 6 | optional bounded-tool/Copilot policy gates | explicit Phase-6 approval/evaluation |

---

# 15. Implementation Definition of Done

- no hard-coded business thresholds outside defaults/schema fixtures;
- deterministic canonical hash;
- explicit schema/version migration path;
- every component receives a typed view from one immutable snapshot;
- invalid policy fails before authoritative work;
- full PRD/ARC/TS/REL traceability retained.
