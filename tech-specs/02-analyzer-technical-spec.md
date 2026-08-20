# TS-ANA — Analyzer A00–A16 Technical Specification

**Document ID:** TS-ANA-001  
**Version:** `2.0.0`
**Date:** 2026-08-14  
**Parent PRD:** `databricks_compute_optimization_product_prd_v2.0.0.md`  
**Parent HLA:** `databricks_compute_optimization_high_level_architecture_v2.0.0.md`  
**Parent requirements:** `PRD-FR-ANA-001..008`, `PRD-FR-ANA-A00-001..A16-001`, `PRD-NFR-ANA-001..004`  
**Architecture:** `ARC-CMP-002`, `ARC-SRC-001`, `ARC-PLAT-002`, `ARC-RUN-001/002/003`  
**Status:** Draft for implementation review  
**Code target:** `src/databricks_compute_optimizer/packs/sql_warehouse/analyzers/ + sql/sql_warehouse/`  

---

# 0. v2.0.0 Architecture Reconciliation

This v2 reconciliation preserves the existing SQL Warehouse business semantics while adopting the Shared Kernel + SQL Warehouse Pack implementation boundary.

- Shared framework/engine code is implemented once under `src/databricks_compute_optimizer/kernel/`.
- SQL Warehouse-specific algorithms, sources, configuration semantics, and providers live under `src/databricks_compute_optimizer/packs/sql_warehouse/`.
- `packs/sql_warehouse/manifest.yaml` points to executable pack capabilities; it is metadata, not duplicate implementation code.
- No future compute pack is implemented by this document.

A00–A16 are SQL Warehouse pack capabilities. The Kernel supplies only the Analyzer execution/result protocol. Every phase-applicable released Analyzer in the SQLWH manifest executes for the authoritative DecisionContext; workload tier cannot suppress one.

Phase-4 references are updated from generic deep-diagnostic enrichment to **SQL Warehouse Deep Diagnostic Intelligence**. Diagnostic evidence must come through an approved SQLWH diagnostic adapter and retain distinct source semantics.

---

# 1. Responsibility and Authority Boundary

The Analyzer converts observed source data into deterministic facts. It owns:

- source metrics;
- derived metrics;
- requested percentiles/distributions;
- signals;
- findings;
- blockers;
- coverage/quality metadata;
- evidence lineage;
- confidence inputs.

The Analyzer MUST NOT:

- choose an optimization candidate;
- predict a counterfactual future state;
- calculate final dollars;
- select an authoritative recommendation;
- infer CPU/memory utilization for SQL warehouses from sources that do not expose those metrics.

The top-level product entity remains `WAREHOUSE`. **A15 is dormant before Phase 5.** Beginning in Phase 5, A15 may analyze an explicitly supplied set of warehouses and derive internal workload groups for O6; those groups are evidence objects, not product-level optimization scopes.

---

# 2. Current Databricks Source Facts Used by This Spec

Validated against official Databricks documentation on 2026-08-14:

| Source | Path | Key fields used | Important semantics |
|---|---|---|---|
| Warehouse config history | `system.compute.warehouses` | warehouse/workspace/account IDs, name, type, channel, size, min/max clusters, auto-stop, tags, change/delete time | each row is a property snapshot; new snapshot on property change; 365-day regional retention |
| Warehouse events | `system.compute.warehouse_events` | warehouse/workspace/account IDs, event_type, cluster_count, event_time | start/stop/run/scale events; 365-day regional retention |
| Query history | `system.query.history` | compute.warehouse_id, status, source/client, durations, timestamps, read/spill/shuffle/task metrics, cache, tags | Public Preview; `start_time` is request receipt, not exact executor start; 365-day regional retention |
| Billing usage | `system.billing.usage` | workspace, SKU, timestamps, quantity/unit, usage_metadata.warehouse_id, record_type, product metadata | global; correction records represented by original/retraction/restatement; aggregate corrected quantities |
| Pricing | `system.billing.list_prices` | SKU, effective interval, pricing.effective_list/default | published historical list price only; use only as configured fallback |
| Warehouse API/SDK/CLI | API fallback / write surface | API-only fields such as `enable_photon`, `enable_serverless_compute`, `spot_instance_policy`, API-only timeout/write semantics, and just-in-time pre-apply current-state verification | **Do not re-fetch size/min/max/auto-stop/type from API when `system.compute.warehouses` resolves them.** Use API only for fields/actions not available from system tables or for pre-write concurrency verification. Exact SDK/API schema is version-pinned. |
| Audit log | `system.access.audit` / audit API | optional editWarehouse fields | enrichment only; audit system table is Public Preview |

References:

- https://docs.databricks.com/aws/en/admin/system-tables/warehouses
- https://docs.databricks.com/aws/en/admin/system-tables/warehouse-events
- https://docs.databricks.com/aws/en/admin/system-tables/query-history
- https://docs.databricks.com/aws/en/admin/system-tables/billing
- https://docs.databricks.com/aws/en/admin/system-tables/pricing
- https://docs.databricks.com/aws/en/admin/system-tables/
- https://docs.databricks.com/aws/en/admin/account-settings/audit-logs
- https://docs.databricks.com/aws/en/dev-tools/cli/reference/warehouses-commands

---

## 2.1 System-table-first source resolution policy

For observation, attribution, historical configuration, and derived metrics, use Databricks system tables before Databricks REST/SDK APIs.

Priority:

```text
1. system tables / governed first-party account telemetry
2. deterministic metrics derived from those tables
3. product-owned persisted derived facts/results
4. Databricks API only when the required field/action is not available from system tables
5. external AWS/enterprise evidence only for economics/security/SLO facts Databricks does not own
```

For SQL Warehouses, `system.compute.warehouses` is the authoritative historical/core configuration source for warehouse type/channel/size/min/max/auto-stop/tags/change history. The Warehouse API remains necessary for API-only fields and for just-in-time read/write verification immediately before an authorized apply action.

If a system table is Preview, Source Coverage/Policy records that maturity and applies the approved capability gate; Preview status alone is not a reason to prefer a redundant API when the product has approved the system-table contract.


---

# 3. Common Analyzer Interface

```python
class Analyzer(Protocol):
    analyzer_id: str
    version: str

    def analyze(
        self,
        request: AnalyzerRequest,
        policy: AnalyzerPolicyView,
        sources: AnalyzerSourceBundle,
    ) -> AnalyzerResult: ...
```

## 3.1 AnalyzerRequest

```json
{
  "run_id": "RUN-...",
  "workspace_id": "WS1",
  "warehouse_id": "WH1",
  "analysis_end_utc": "2026-08-12T00:00:00Z",
  "windows_days": [7, 30, 90, 365],
  "requested_percentiles": [50, 95, 99],
  "participating_warehouse_ids": null,
  "reason": "WEEKLY|SELECTIVE|VALIDATION|TOPOLOGY"
}
```

`participating_warehouse_ids` is used only by analyzers such as A15 when O6 explicitly requests multi-warehouse evidence.

## 3.2 AnalyzerResult

```json
{
  "contract_version": "1.0.0",
  "analyzer_result_id": "AR-A07-...",
  "analyzer_id": "A07",
  "analyzer_version": "1.0.0",
  "warehouse_id": "WH1",
  "participating_warehouse_ids": [],
  "observation_window": {"start_utc": "...", "end_utc": "..."},
  "source_metrics": [
    {"metric_id": "...", "value": 0, "unit": "ms", "source_ref": "SRC-DBX-003", "query_id": "Q-ANA-..."}
  ],
  "derived_metrics": [
    {"metric_id": "...", "value": 0, "unit": "%", "formula_id": "F-ANA-...", "input_metric_refs": []}
  ],
  "distributions": [
    {"metric_id": "capacity_wait_ms", "p50": 0, "p95": 0, "p99": 0, "sample_size": 1000, "method": "percentile_approx", "accuracy": 10000}
  ],
  "signals": [],
  "findings": [],
  "blockers": [],
  "confidence_inputs": {},
  "data_quality": {},
  "lineage": {},
  "policy_snapshot_id": "PSNAP-...",
  "status": "SUCCESS|PARTIAL|BLOCKED"
}
```

---

# 4. Metric Semantics

## 4.1 Percentiles

Required where meaningful:

- P50 = normal/typical behavior;
- P95 = primary sizing/decision behavior;
- P99 = risk/tail behavior.

For large source volumes, SQL MAY use `percentile_approx` with a fixed Policy-controlled accuracy. For bounded golden fixtures, exact pandas quantiles SHOULD be used to assert expected values. Method/accuracy/sample size must be recorded.

If sample size is below Policy minimum, Analyzer MUST emit `INSUFFICIENT_SAMPLE` and not fabricate P95/P99.

## 4.2 Time semantics

- internally normalize to UTC;
- retain local/calendar context for seasonality;
- `system.query.history.start_time` means request receipt;
- request-overlap concurrency is therefore a **demand concurrency** metric, not hardware executor concurrency;
- any execution-overlap reconstruction must be explicitly labeled a proxy and cannot be presented as CPU/core utilization.

---

# 5. Source Query Catalog

All queries are parameterized and bounded. Query adapters MUST add workspace/warehouse/date predicates wherever the source supports them.

## Q-ANA-001 — current core warehouse configuration

```sql
SELECT
  account_id,
  workspace_id,
  warehouse_id,
  warehouse_name,
  warehouse_type,
  warehouse_channel,
  warehouse_size,
  min_clusters,
  max_clusters,
  auto_stop_minutes,
  tags,
  change_time,
  delete_time
FROM system.compute.warehouses
WHERE workspace_id = :workspace_id
  AND warehouse_id = :warehouse_id
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY workspace_id, warehouse_id
  ORDER BY change_time DESC
) = 1
AND delete_time IS NULL;
```

Source authority follows Databricks' documented latest-`change_time` pattern.

## Q-ANA-002 — configuration eras

```sql
WITH cfg AS (
  SELECT
    workspace_id,
    warehouse_id,
    warehouse_type,
    warehouse_channel,
    warehouse_size,
    min_clusters,
    max_clusters,
    auto_stop_minutes,
    tags,
    change_time AS era_start_utc,
    LEAD(change_time) OVER (
      PARTITION BY workspace_id, warehouse_id
      ORDER BY change_time
    ) AS next_change_utc,
    delete_time
  FROM system.compute.warehouses
  WHERE workspace_id = :workspace_id
    AND warehouse_id = :warehouse_id
    AND change_time < :end_ts
)
SELECT *,
       COALESCE(next_change_utc, :end_ts) AS era_end_utc
FROM cfg
WHERE COALESCE(next_change_utc, :end_ts) > :start_ts
  AND (delete_time IS NULL OR delete_time >= :start_ts)
ORDER BY era_start_utc;
```

API-only fields are joined as supplemental snapshots/history only when a trustworthy historical source is available. Current-only API fields MUST NOT be backfilled historically by assumption.

## Q-ANA-003 — bounded query-history base

```sql
SELECT
  workspace_id,
  statement_id,
  session_id,
  execution_status,
  compute.warehouse_id AS warehouse_id,
  statement_type,
  error_message,
  client_application,
  client_driver,
  total_duration_ms,
  waiting_for_compute_duration_ms,
  waiting_at_capacity_duration_ms,
  execution_duration_ms,
  compilation_duration_ms,
  total_task_duration_ms,
  start_time,
  end_time,
  read_partitions,
  pruned_files,
  read_files,
  read_rows,
  produced_rows,
  read_bytes,
  read_io_cache_percent,
  from_result_cache,
  spilled_local_bytes,
  written_bytes,
  written_rows,
  written_files,
  shuffle_read_bytes,
  query_source,
  query_tags
FROM system.query.history
WHERE workspace_id = :workspace_id
  AND compute.type = 'WAREHOUSE'
  AND compute.warehouse_id = :warehouse_id
  AND start_time >= :start_ts
  AND start_time < :end_ts;
```

`statement_text` is intentionally omitted from the default extractor. A policy-approved workload-fingerprinting query may add a hashed/normalized representation without persisting raw SQL text.

## Q-ANA-004 — query performance percentile aggregation

```sql
SELECT
  COUNT(*) AS query_count,
  percentile_approx(total_duration_ms, array(0.50, 0.95, 0.99), :pct_accuracy) AS total_ms_p,
  percentile_approx(waiting_for_compute_duration_ms, array(0.50, 0.95, 0.99), :pct_accuracy) AS provision_wait_ms_p,
  percentile_approx(waiting_at_capacity_duration_ms, array(0.50, 0.95, 0.99), :pct_accuracy) AS capacity_wait_ms_p,
  percentile_approx(execution_duration_ms, array(0.50, 0.95, 0.99), :pct_accuracy) AS execution_ms_p,
  percentile_approx(total_task_duration_ms, array(0.50, 0.95, 0.99), :pct_accuracy) AS task_ms_p,
  percentile_approx(spilled_local_bytes, array(0.50, 0.95, 0.99), :pct_accuracy) AS spill_bytes_p,
  percentile_approx(read_bytes, array(0.50, 0.95, 0.99), :pct_accuracy) AS read_bytes_p,
  percentile_approx(shuffle_read_bytes, array(0.50, 0.95, 0.99), :pct_accuracy) AS shuffle_bytes_p
FROM system.query.history
WHERE workspace_id = :workspace_id
  AND compute.type = 'WAREHOUSE'
  AND compute.warehouse_id = :warehouse_id
  AND start_time >= :start_ts
  AND start_time < :end_ts;
```

## Q-ANA-005 — query demand buckets

```sql
SELECT
  date_trunc(:bucket, start_time) AS bucket_start_utc,
  COUNT(*) AS arrivals,
  SUM(CASE WHEN execution_status = 'FINISHED' THEN 1 ELSE 0 END) AS finished,
  AVG(total_duration_ms) AS avg_total_duration_ms,
  MAX(waiting_at_capacity_duration_ms) AS max_capacity_wait_ms
FROM system.query.history
WHERE workspace_id = :workspace_id
  AND compute.type = 'WAREHOUSE'
  AND compute.warehouse_id = :warehouse_id
  AND start_time >= :start_ts
  AND start_time < :end_ts
GROUP BY 1
ORDER BY 1;
```

`:bucket` is selected from an allowlist (`minute`, `5-minute implementation bucket`, `hour`, `day`) by the query builder; never interpolate arbitrary SQL.

## Q-ANA-006 — request concurrency event sweep source

```sql
WITH events AS (
  SELECT start_time AS ts, 1 AS delta
  FROM system.query.history
  WHERE workspace_id = :workspace_id
    AND compute.type = 'WAREHOUSE'
    AND compute.warehouse_id = :warehouse_id
    AND start_time >= :start_ts AND start_time < :end_ts

  UNION ALL

  SELECT end_time AS ts, -1 AS delta
  FROM system.query.history
  WHERE workspace_id = :workspace_id
    AND compute.type = 'WAREHOUSE'
    AND compute.warehouse_id = :warehouse_id
    AND end_time >= :start_ts AND end_time < :end_ts
), grouped AS (
  SELECT ts, SUM(delta) AS delta
  FROM events
  GROUP BY ts
), sweep AS (
  SELECT
    ts,
    SUM(delta) OVER (ORDER BY ts ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS request_concurrency
  FROM grouped
)
SELECT * FROM sweep ORDER BY ts;
```

This is request occupancy/demand concurrency, not executor concurrency.

## Q-ANA-007 — warehouse events

```sql
SELECT
  workspace_id,
  warehouse_id,
  event_type,
  cluster_count,
  event_time
FROM system.compute.warehouse_events
WHERE workspace_id = :workspace_id
  AND warehouse_id = :warehouse_id
  AND event_time >= :start_ts
  AND event_time < :end_ts
ORDER BY event_time;
```

## Q-ANA-008 — event state intervals

Phase 1 retrieves Q-ANA-007 and reconstructs intervals deterministically in pandas because interval semantics are easier to test than a large SQL CTE. Each event row becomes a state boundary; next event time closes the interval; analysis end closes an open terminal interval.

Derived interval fields:

```text
interval_start
interval_end
state_event_type
cluster_count
interval_seconds
is_running
```

`RUNNING` and non-stopped scaled states are interpreted according to a versioned state-machine helper; invalid sequences generate warnings/blockers instead of guessed states.

## Q-ANA-009 — corrected warehouse billable quantities

```sql
SELECT
  workspace_id,
  usage_metadata.warehouse_id AS warehouse_id,
  sku_name,
  usage_unit,
  usage_date,
  SUM(usage_quantity) AS corrected_usage_quantity,
  COUNT(*) AS billing_record_count,
  SUM(CASE WHEN record_type = 'RETRACTION' THEN 1 ELSE 0 END) AS retraction_count,
  SUM(CASE WHEN record_type = 'RESTATEMENT' THEN 1 ELSE 0 END) AS restatement_count
FROM system.billing.usage
WHERE usage_metadata.warehouse_id = :warehouse_id
  AND usage_start_time >= :start_ts
  AND usage_start_time < :end_ts
GROUP BY workspace_id, usage_metadata.warehouse_id, sku_name, usage_unit, usage_date;
```

Databricks correction semantics are handled by summing `usage_quantity`; A01 retains correction counts as quality evidence.

## Q-ANA-010 — list-price fallback intervals

```sql
SELECT
  sku_name,
  cloud,
  currency_code,
  usage_unit,
  price_start_time,
  price_end_time,
  pricing.effective_list.default AS effective_list_price,
  pricing.default AS default_list_price
FROM system.billing.list_prices
WHERE cloud = 'AWS'
  AND price_start_time < :end_ts
  AND COALESCE(price_end_time, TIMESTAMP '9999-12-31') >= :start_ts;
```

This source is a published list-price fallback and must never be mislabeled as negotiated actual rate.

## Q-ANA-011 — reliability aggregation

```sql
SELECT
  COUNT(*) AS total_queries,
  SUM(CASE WHEN execution_status = 'FINISHED' THEN 1 ELSE 0 END) AS finished_queries,
  SUM(CASE WHEN execution_status = 'FAILED' THEN 1 ELSE 0 END) AS failed_queries,
  SUM(CASE WHEN execution_status = 'CANCELED' THEN 1 ELSE 0 END) AS canceled_queries
FROM system.query.history
WHERE workspace_id = :workspace_id
  AND compute.type = 'WAREHOUSE'
  AND compute.warehouse_id = :warehouse_id
  AND start_time >= :start_ts
  AND start_time < :end_ts;
```

Error classification uses deterministic regex/category rules only for known patterns; unmatched errors are `UNKNOWN`, never guessed.

## Q-ANA-012 — hourly/daily seasonal profile

```sql
SELECT
  dayofweek(start_time) AS day_of_week,
  hour(start_time) AS hour_of_day,
  COUNT(*) AS query_count,
  SUM(total_task_duration_ms) AS task_ms,
  SUM(read_bytes) AS read_bytes,
  SUM(waiting_at_capacity_duration_ms) AS capacity_wait_ms
FROM system.query.history
WHERE workspace_id = :workspace_id
  AND compute.type = 'WAREHOUSE'
  AND compute.warehouse_id = :warehouse_id
  AND start_time >= :start_ts
  AND start_time < :end_ts
GROUP BY dayofweek(start_time), hour(start_time);
```

## Q-ANA-013 — long-tail extraction

```sql
SELECT
  statement_id,
  statement_type,
  query_source,
  query_tags,
  start_time,
  total_duration_ms,
  execution_duration_ms,
  total_task_duration_ms,
  read_bytes,
  spilled_local_bytes,
  shuffle_read_bytes,
  execution_status
FROM system.query.history
WHERE workspace_id = :workspace_id
  AND compute.type = 'WAREHOUSE'
  AND compute.warehouse_id = :warehouse_id
  AND start_time >= :start_ts
  AND start_time < :end_ts
  AND total_duration_ms >= :long_tail_floor_ms
ORDER BY total_duration_ms DESC
LIMIT :max_tail_rows;
```

---

# 6. Analyzer Catalog Summary

| ID | Analyzer | Primary sources | Required distributions | Key consumers |
|---|---|---|---|---|
| A00 | Data Coverage & Attribution | all | coverage/freshness | all |
| A01 | Cost Usage & Attribution | billing, list price, commercial rates, AWS CUR | cost-quantity coverage | Estimator, Tiering |
| A02 | Effective Warehouse Configuration | warehouses + API | config eras | all optimizers, Lifecycle |
| A03 | Demand & Concurrency | query history | arrivals/concurrency P50/P95/P99 | O2, O6, Modeler |
| A04 | Idle / Auto-Stop | query history + events | gaps/idle P50/P95/P99 | O3, Modeler |
| A05 | Runtime / SLA | query history + SLO | runtime/waits/task P50/P95/P99 | O1/O2/O3/O5/O6, Lifecycle |
| A06 | Resource Pressure | query history; Phase-4 SQLWH deep diagnostic evidence | spill/read/shuffle/task P50/P95/P99 | O2/O5/O6 |
| A07 | Queue / Capacity | query history + events | capacity wait/concurrency | O2/O6 |
| A08 | Scaling Efficiency | events + config | cluster-count/intervals | O2/O3/O4 |
| A09 | Cold-Start Sensitivity | events + query history | startup/provision wait | O1/O3 |
| A10 | Warehouse-Type Eligibility | config/API + org eligibility | N/A | O1 |
| A11 | Reliability | query history + optional API/audit + Phase-4 SQLWH diagnostic evidence | failure/cancel/retry rates | O1/O2/O4/O5/O6/Lifecycle |
| A12 | Seasonality & Workload Regime | query history | temporal distributions | Modeler, all major optimizers |
| A13 | Spot Economics | AWS CUR/pricing + reliability | cost/risk evidence | O4 |
| A14 | Photon Effectiveness | API/audit/config-era + query history + billing | matched runtime/cost | O5 |
| A15 | Workload Affinity / Topology | multiple warehouses' query/config/SLO/security | overlap/affinity | O6 |
| A16 | Runaway Query Tail | query history + SLO | tail ratios | O7 |

---

# 7. A00 — Data Coverage & Attribution

**TS ID:** `TS-ANA-A00-001`

## Purpose

Prove that the observation window and required joins are sufficiently complete to support authoritative analysis.

## Source metrics

- min/max timestamp per required source;
- daily row count per source;
- config era coverage;
- query-history active days;
- billing active days;
- warehouse-attributed billing quantity share;
- AWS CUR attribution share for Pro/Classic;
- source ingestion/freshness metadata where available.

## Derived metrics

```text
window_coverage_pct = observed_expected_time_buckets / expected_time_buckets * 100
warehouse_billing_attribution_pct = warehouse_attributed_cost_or_quantity / eligible_sql_warehouse_total * 100
config_interval_coverage_pct = covered_seconds / observation_window_seconds * 100
```

Coverage is a documented assessment method, not a claim that Databricks emitted every logically possible event.

## Signals

- `SOURCE_FRESH`
- `SOURCE_STALE`
- `QUERY_HISTORY_GAP`
- `BILLING_GAP`
- `CONFIG_GAP`
- `AWS_ATTRIBUTION_LOW`

## Findings / blockers

- `EVIDENCE_COVERAGE_SUFFICIENT`
- `MATERIAL_DATA_GAP`
- blocker `REQUIRED_SOURCE_MISSING`
- blocker `CONFIG_HISTORY_INCOMPLETE`
- blocker `FINANCIAL_ATTRIBUTION_INSUFFICIENT`

A00 blocker scope is only the affected warehouse/technique; do not halt unrelated warehouses.

---

# 8. A01 — Cost Usage & Attribution

**TS ID:** `TS-ANA-A01-001`

## Purpose

Produce `CostEvidence`; do not calculate authoritative dollars.

## Inputs

- Q-ANA-009 corrected billable quantities;
- negotiated/effective rate references;
- Q-ANA-010 list-price fallback;
- AWS CUR 2.0 rows attributed by Databricks SQL warehouse tags (`SqlEndpointId`, `ClusterId`) and resource IDs where available;
- commitment metadata (Savings Plans/RI) from CUR;
- A00 coverage.

Databricks default SQL warehouse tags propagate to AWS EC2/EBS resources and include `SqlEndpointId`, enabling direct warehouse attribution where configured as cost-allocation tags.

## Output `CostEvidence`

```json
{
  "warehouse_id": "WH1",
  "databricks_usage": [
    {"date": "...", "sku_name": "...", "usage_unit": "DBU", "corrected_quantity": "12.345"}
  ],
  "rate_refs": [],
  "aws_attributed_rows_ref": "...",
  "aws_attribution_pct": 99.2,
  "commitment_characteristics": {},
  "billing_reconciled": true,
  "blockers": []
}
```

## Blockers

- unreconciled corrections;
- material warehouse ID gaps;
- missing commercial rate plus policy forbids list-price authority;
- material AWS attribution gap for Pro/Classic.

---

# 9. A02 — Effective Warehouse Configuration

**TS ID:** `TS-ANA-A02-001`

## Purpose

Reconstruct point-in-time config eras and canonical current configuration.

## Core source fields

From `system.compute.warehouses`:

- `warehouse_type`
- `warehouse_channel`
- `warehouse_size`
- `min_clusters`
- `max_clusters`
- `auto_stop_minutes`
- tags
- `change_time`, `delete_time`.

Supplement current fields from API:

- Photon state;
- serverless enablement flag / canonical type mapping;
- Spot policy;
- statement timeout when supported/enabled;
- any current field required by an optimizer and exposed by pinned SDK schema.

## Canonical mapping

```text
API warehouse_type=PRO + enable_serverless_compute=true → canonical type SERVERLESS
API warehouse_type=PRO + enable_serverless_compute=false → PRO
API warehouse_type=CLASSIC → CLASSIC
```

No historical Photon/Spot state is inferred from the present API state. Historical evidence requires audit/history or a recorded optimizer/lifecycle snapshot.

## Blockers

- conflicting current core config between sources without resolvable timestamp ordering;
- required API field unavailable for optimizer;
- invalid min/max relationship;
- unsupported/unrecognized warehouse type.

---

# 10. A03 — Demand & Concurrency

**TS ID:** `TS-ANA-A03-001`

## Metrics

- queries/minute, queries/5-minute, queries/hour;
- arrival P50/P95/P99;
- request concurrency P50/P95/P99 from event sweep;
- burst ratio = P99 / max(P50, epsilon);
- client/source/query-tag mix;
- peak recurrence by hour-of-week;
- growth evidence by A12 regime.

## Important semantics

`start_time` is request receipt. Therefore request concurrency measures submitted/in-flight demand. It must not be described as exact executor/core concurrency.

## Signals

- `HIGH_BURSTINESS`
- `STABLE_DEMAND`
- `HIGH_PEAK_CONCURRENCY`
- `CONCURRENCY_GROWTH`

## Consumers

O2 uses demand distribution; O6 uses time-aligned workload demand; Modeler uses temporal profiles.

---

# 11. A04 — Idle / Auto-Stop

**TS ID:** `TS-ANA-A04-001`

## Derived timeline

1. reconstruct warehouse running intervals from Q-ANA-007;
2. create query activity intervals from query history;
3. clip query intervals to running intervals;
4. compute gaps between query activity while warehouse is running;
5. derive idle seconds and candidate timeout replay inputs.

Metrics:

- inter-request gap P50/P95/P99;
- running seconds;
- busy seconds;
- idle-running seconds;
- idle fraction;
- restart count;
- queries following starts within configurable cold window;
- avoidable idle seconds by candidate timeout (input to Modeler/Estimator; not dollars here).

Signals:

- `MATERIAL_IDLE_RUNNING`
- `FREQUENT_SHORT_GAPS`
- `COLD_START_SENSITIVE`
- `AUTOSTOP_ALREADY_EFFICIENT`

---

# 12. A05 — Runtime / SLA Baseline

**TS ID:** `TS-ANA-A05-001`

Metrics by workload cohort and current regime:

- total duration P50/P95/P99;
- execution duration P50/P95/P99;
- provisioning wait P50/P95/P99;
- capacity wait P50/P95/P99;
- task duration P50/P95/P99;
- normalized runtime vs read bytes/read rows where appropriate;
- SLO target and headroom from organization adapter;
- cache-hit split where material.

Do not combine provisioning and capacity wait into one metric for decisions.

Derived:

```text
runtime_headroom_pct = (SLO_p95_ms - observed_p95_ms) / SLO_p95_ms * 100
capacity_wait_share = capacity_wait_ms / max(total_duration_ms, 1)
provision_wait_share = provision_wait_ms / max(total_duration_ms, 1)
```

Signals:

- `RUNTIME_HEADROOM_HIGH|LOW`
- `PROVISIONING_DOMINANT`
- `CAPACITY_WAIT_DOMINANT`
- `TAIL_RUNTIME_HIGH`

---

# 13. A06 — Resource Pressure

**TS ID:** `TS-ANA-A06-001`

Phase-1 documented SQL telemetry:

- `spilled_local_bytes`
- `read_bytes`, `read_rows`, `read_files`, `read_partitions`
- `shuffle_read_bytes`
- `total_task_duration_ms`
- cache percentage
- written bytes/rows/files when relevant.

Derived:

```text
spill_per_read_byte = spilled_local_bytes / max(read_bytes, 1)
task_ms_per_gb_read = total_task_duration_ms / max(read_bytes / 1e9, epsilon)
shuffle_to_read_ratio = shuffle_read_bytes / max(read_bytes, 1)
```

Signals:

- `MATERIAL_SPILL`
- `HIGH_SHUFFLE_INTENSITY`
- `HIGH_TASK_INTENSITY`
- `LOW_RESOURCE_PRESSURE_EVIDENCE`

**Prohibition:** no CPU%, memory%, executor-memory utilization, or node-memory claims from query history.

Phase 4 may enrich A06 with SQLWH Deep Diagnostic Intelligence under the same evidence contract. New fields MUST use an approved diagnostic source label/capability ID and retain source lineage.

---

# 14. A07 — Queue / Capacity

**TS ID:** `TS-ANA-A07-001`

Metrics:

- capacity wait P50/P95/P99;
- fraction of queries with `waiting_at_capacity_duration_ms > 0`;
- total capacity-wait seconds;
- request concurrency P95/P99;
- event-derived time at configured max clusters;
- queue evidence during intervals at max clusters;
- peak queued-query proxy from query history (not UI-only metric unless API source added).

Derived:

```text
capacity_queue_rate = queries_with_capacity_wait / total_queries
at_max_cluster_pct = seconds_at_max / running_seconds
queue_while_at_max_pct = queued_query_time_during_max / total_queued_query_time
```

Signals:

- `CAPACITY_CONSTRAINED`
- `MAX_CLUSTER_SATURATED`
- `QUEUE_WITH_HEADROOM`
- `LITTLE_CAPACITY_WAIT`

O2 must consider size and max clusters jointly; Analyzer does not decide which to change.

---

# 15. A08 — Scaling Efficiency

**TS ID:** `TS-ANA-A08-001`

Inputs: warehouse event intervals + effective config eras.

Metrics:

- cluster-seconds = Σ(cluster_count × interval_seconds);
- running seconds;
- time at min clusters;
- time at max clusters;
- scale-up count;
- scale-down count;
- scale transitions/hour;
- high-cluster intervals during low demand;
- scale-out duration distribution.

Signals:

- `HIGH_SCALE_CHURN`
- `LONG_TIME_AT_MAX`
- `LONG_TIME_ABOVE_MIN_LOW_DEMAND`
- `SCALING_EFFICIENT`

Note: Databricks can temporarily exceed configured max during periodic cluster recycling; the implementation must not automatically classify a brief max+1 interval as policy violation. Current Databricks docs explicitly describe this recycling behavior.

---

# 16. A09 — Cold-Start Sensitivity

**TS ID:** `TS-ANA-A09-001`

Startup interval:

```text
STARTING event → first subsequent RUNNING event
```

Metrics:

- startup duration P50/P95/P99;
- starts/day/week;
- first-query provisioning wait after start;
- warm-query provisioning wait;
- cold-vs-warm total runtime distributions;
- percentage of queries affected by recent start.

If event sequences are incomplete, startup metrics are partial/blocked rather than guessed.

Signals:

- `COLD_START_HIGH_IMPACT`
- `FREQUENT_RESTARTS`
- `STARTUP_FAST`

Serverless and Pro/Classic are compared empirically; documented typical startup times are eligibility/context, not substituted for observed warehouse measurements.

---

# 17. A10 — Warehouse-Type Eligibility

**TS ID:** `TS-ANA-A10-001`

Eligibility is deterministic and uses platform capability + enterprise environment facts.

Candidate types:

- `CLASSIC`
- `PRO`
- `SERVERLESS`
- gated `LAKEHOUSE_REALTIME` only if future policy/capability allows.

Serverless checks include current documented requirements/limitations such as:

- account/workspace eligibility;
- Premium or higher plan;
- no workspace S3 access policies;
- no external legacy Hive metastore;
- custom networking/compliance requirements compatible with serverless;
- no dependency on unsupported cluster/Spot policy behavior;
- security/CMK rules accepted by organization policy.

Lakehouse Real-Time is Beta and SELECT-only as of validation date; production target is OFF by default.

Output:

```json
{
  "type_eligibility": {
    "CLASSIC": {"eligible": true, "reasons": []},
    "PRO": {"eligible": true, "reasons": []},
    "SERVERLESS": {"eligible": false, "reasons": ["CUSTOM_NETWORK_REQUIREMENT"]}
  }
}
```

A10 does not decide which eligible type is cheapest; O1 does.

---

# 18. A11 — Reliability

**TS ID:** `TS-ANA-A11-001`

Metrics:

- finish/fail/cancel rate;
- error category frequencies;
- retry proxy only when repeat execution can be linked reliably;
- config-era reliability rates;
- confidence intervals for low-frequency failures.

Error categories are a versioned registry. Example categories:

- permission/authentication;
- syntax/semantic;
- resource/capacity;
- timeout;
- data/source;
- user cancel;
- unknown.

Never infer Spot interruption solely from a generic query failure.

Signals:

- `RELIABILITY_STABLE`
- `FAILURE_RATE_ELEVATED`
- `UNKNOWN_FAILURE_CAUSE_HIGH`

---

# 19. A12 — Seasonality & Workload Regime

**TS ID:** `TS-ANA-A12-001`

Phase-1 algorithm classes:

- hourly/daily/weekly profiles;
- month-end/quarter-end flags;
- rolling 7/30/90/365 summaries;
- deterministic change-point/regime detection;
- daily volume/runtime trend.

Recommended deterministic change-point baseline:

1. aggregate daily demand/cost-driver metrics;
2. compute rolling median and MAD;
3. flag sustained shift when median of recent policy window differs from prior baseline by policy threshold for policy minimum days;
4. choose most recent stable regime that satisfies minimum sample and coverage.

Output:

- `current_regime_start`;
- `regime_stable`;
- `seasonal_indices`;
- `trend_slope`;
- `peak_periods`;
- `recent_window_representative` boolean.

Modeler owns forward projection; A12 owns observed pattern/regime facts.

---

# 20. A13 — Spot Economics

**TS ID:** `TS-ANA-A13-001`

Applies to Pro/Classic only.

Sources:

- current Spot policy from API;
- AWS CUR actual EC2/EBS economics attributed by warehouse tags/resources;
- optional AWS Spot price/interruption evidence if available through approved adapter;
- A11 reliability and retry evidence.

Output facts:

- current Spot policy;
- AWS economic cost by resource family/time;
- commitment coverage characteristics;
- observed failure/retry evidence coincident with infrastructure changes only where attribution is defensible;
- causal confidence.

For Serverless, result status is `NOT_APPLICABLE` evidence for O4.

---

# 21. A14 — Photon Effectiveness

**TS ID:** `TS-ANA-A14-001`

Sources:

- current Photon API field;
- audit/config snapshots if available historically;
- matched query/workload cohorts by Photon config era;
- A05/A06 runtime/resource evidence;
- A01 cost-quantity evidence.

Preferred evidence hierarchy:

1. same workload under both Photon states within comparable regime;
2. controlled canary/benchmark;
3. approved statistical counterfactual with sufficient matched evidence;
4. otherwise `INSUFFICIENT_COMPARISON`.

Analyzer emits matched evidence; Modeler may predict candidate behavior; O5 decides.

---

# 22. A15 — Workload Affinity / Topology

**TS ID:** `TS-ANA-A15-001`

A15 is the only Analyzer intentionally designed for multi-warehouse inputs, and it activates only in **Phase 5**.

## Scope rule

Input is still an explicit list of warehouse IDs. A15 may derive internal `workload_group_id` objects for analytical/routing purposes. This does **not** create a new top-level optimization scope.

## Workload grouping inputs

Default privacy-preserving attributes:

- `query_source` IDs/types;
- `client_application`;
- `statement_type`;
- query tags;
- temporal pattern;
- read/task/spill profile;
- runtime/SLO class;
- optional policy-approved statement fingerprint.

## Pairwise warehouse features

- peak-time overlap;
- concurrency correlation;
- workload-class compatibility;
- SLO compatibility;
- security/network/ACL compatibility;
- duplicate idle/warm cost evidence;
- resource profile similarity;
- interference evidence;
- cost concentration.

Derived examples:

```text
overlap_ratio = simultaneous_peak_buckets / union_peak_buckets
idle_duplication_seconds = sum(idle_running_seconds across warehouses during compatible low-demand periods)
resource_profile_distance = deterministic normalized distance across approved feature vector
```

Compatibility hard gates come before affinity scores.

Output:

```json
{
  "participating_warehouse_ids": ["WH-A", "WH-B"],
  "workload_groups": [],
  "pairwise_evidence": [],
  "compatibility": {"security": "PASS", "network": "PASS", "slo": "PASS"},
  "signals": ["CONSOLIDATION_EVIDENCE"],
  "blockers": []
}
```

O6 alone generates the topology candidate.

---

# 23. A16 — Runaway Query Tail

**TS ID:** `TS-ANA-A16-001`

Goal: identify plausible pathological long-tail queries while protecting legitimate long-running work.

Baseline method:

1. group queries by deterministic workload class/fingerprint;
2. normalize for read volume where appropriate;
3. calculate cohort P50/P95/P99 and robust MAD/IQR;
4. mark a candidate tail query only when duration materially exceeds both cohort tail threshold and absolute policy floor;
5. exclude known scheduled/approved long-running classes/SLOs;
6. estimate historical wasted task/runtime quantity after proposed timeout threshold as **protective** evidence only.

Signals:

- `RUNAWAY_TAIL_PRESENT`
- `LEGITIMATE_LONG_RUNNING_CLASS`
- `TIMEOUT_FALSE_POSITIVE_RISK`

O7 remains disabled by default because warehouse-level statement timeout is Beta as of source validation.

---

# 24. Analyzer → Optimizer Dependency Matrix

| Analyzer | O1 | O2 | O3 | O4 | O5 | O6 | O7 |
|---|---:|---:|---:|---:|---:|---:|---:|
| A00 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| A01 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| A02 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| A03 | ✓ | ✓ |  |  |  | ✓ |  |
| A04 |  |  | ✓ |  |  | ✓ |  |
| A05 | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ |
| A06 |  | ✓ |  |  | ✓ | ✓ | ✓ |
| A07 |  | ✓ |  |  |  | ✓ |  |
| A08 |  | ✓ | ✓ | ✓ |  | ✓ |  |
| A09 | ✓ |  | ✓ |  |  |  |  |
| A10 | ✓ |  |  | ✓ applicability |  | ✓ | ✓ feature gate |
| A11 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| A12 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| A13 |  |  |  | ✓ |  |  |  |
| A14 |  |  |  |  | ✓ |  |  |
| A15 |  |  |  |  |  | ✓ |  |
| A16 |  |  |  |  |  |  | ✓ |

Estimator/Modeler may consume analyzer results separately according to their specs.

---

# 25. Blocker Rules

A blocker is emitted when missing/ambiguous evidence could reverse a decision or violate a hard requirement.

Examples:

| Analyzer | Blocker example |
|---|---|
| A00 | required source gap exceeds policy |
| A01 | financial attribution insufficient |
| A02 | effective config unresolved |
| A05 | performance baseline sample insufficient for performance-sensitive candidate |
| A10 | target type violates enterprise eligibility |
| A11 | reliability evidence unavailable where reliability guardrail is required |
| A15 | security/network compatibility unknown |
| A16 | legitimate long-running queries cannot be separated from suspected runaways |

Low confidence is not a substitute for a blocker when the missing fact can reverse the recommendation.

---

# 26. Phase-1 Pandas Implementation Rules

- push aggregation/filtering to SQL whenever possible;
- raw query history extracts must be bounded by warehouse + time + row/candidate need;
- use Arrow fetch path from Databricks SQL connector where available;
- transform functions must be pure and typed;
- use `Decimal` for financial quantities passed to A01/Estimator;
- no component stores raw query text by default;
- no intermediate Delta tables required;
- authoritative result artifacts are compact JSON/Parquet through `StateRepository`.

System tables can add columns/struct fields; selectors MUST enumerate required columns and ignore compatible additions rather than use brittle `SELECT *` schemas.

---

# 27. Phase-4 SQL Warehouse Deep Diagnostic Enrichment

Phase 4 may add SQLWH diagnostic evidence to:

- A06 resource pressure;
- A11 failure/execution diagnostics;
- A14 Photon/completed-work analysis where applicable;
- candidate Modeler features.

Rules:

1. SQL-system-table logic remains available as fallback.
2. Diagnostic-derived metrics must be clearly source-labeled.
3. Phase-4 enrichment cannot change earlier contract meanings without a version bump.
4. SQLWH deep diagnostic evidence do not authorize SQL/query rewrite recommendations.

---

# 27.1 Capability Registry and DecisionContext integration

- Each Analyzer implementation is registered once in `packs/sql_warehouse/manifest.yaml`.
- The Kernel Analyzer framework resolves the applicable released Analyzer set from `CapabilityRegistrySnapshot`.
- All applicable Analyzers execute deterministically; T1–T4 does not remove them.
- Analyzer result digests and versions contribute to DecisionContext.
- An LLM cannot ask an already applicable Analyzer to rerun against the same context.
- New Analyzer semantics discovered by review enter `CapabilityGap`; only a released new Analyzer changes the applicable capability set.

---

# 28. Observability

Per analyzer emit:

- rows scanned/returned where available;
- source query duration;
- observation window;
- sample sizes;
- requested/calculated percentile method;
- source freshness;
- metric count;
- signals/findings/blockers count;
- output hash;
- retry/failure code.

A00 aggregates source-level quality metrics for the run.

---

# 29. Error Semantics

| Code | Meaning |
|---|---|
| `ANA_SOURCE_UNAVAILABLE` | required source adapter failed |
| `ANA_INSUFFICIENT_SAMPLE` | percentile/metric not statistically supported |
| `ANA_EVENT_SEQUENCE_INVALID` | warehouse event state cannot be safely reconstructed |
| `ANA_CONFIG_AMBIGUOUS` | effective config conflict |
| `ANA_UNSUPPORTED_FIELD` | required field absent in pinned source schema |
| `ANA_PRIVACY_POLICY_BLOCK` | raw SQL/fingerprint use disallowed |
| `ANA_COVERAGE_BLOCKED` | A00 material coverage failure |

---

# 30. Test Strategy

Each analyzer requires:

- unit formula tests;
- empty/sparse data tests;
- percentile exact fixture tests;
- window boundary/timezone tests;
- duplicated/retraction/restatement billing fixtures for A01;
- event-sequence fixtures for A04/A08/A09;
- current/config-era fixtures for A02/A14;
- eligibility matrix fixtures for A10;
- mixed errors/unknown errors for A11;
- seasonality/change-point fixtures for A12;
- topology compatibility/overlap fixtures for A15;
- legitimate long-running vs runaway fixtures for A16;
- deterministic replay equality tests.

Golden E2E scenarios downstream will assert cross-analyzer combinations, not replace component tests.

---

# 31. Component Release Plan

| Release | Analyzer scope | Exit criteria |
|---|---|---|
| `REL-ANA-0.1.0` | A00 coverage, A01 cost evidence, A02 effective config | source contracts + baseline Estimator can run |
| `REL-ANA-0.2.0` | A03 demand, A04 idle, A05 runtime | O2/O3/statistical Modeler evidence available |
| `REL-ANA-0.3.0` | A06 resource pressure, A07 queue, A08 scaling, A09 cold start | capacity/autostop/type performance evidence complete |
| `REL-ANA-0.4.0` | A10 eligibility, A11 reliability, A12 regime | O1/guardrail/forward modeling ready |
| `REL-ANA-0.5.0` | A13 Spot, A14 Photon, A16 runaway tail | all Phase-1 O1–O5/O7 evidence supported |
| `REL-ANA-1.0.0` | Phase-1 contract freeze, performance/observability hardening | all analyzer component/golden fixtures pass |
| `REL-ANA-2.0.0` | Phase-2 PySpark/Delta backend parity | pandas↔PySpark Analyzer parity passes |
| `REL-ANA-4.0.0` | Phase-4 SQLWH Deep Diagnostic enrichment | source/feature/fallback tests; no earlier semantic regression |
| `REL-ANA-5.0.0` | A15 workload affinity/topology | Phase-5 O6 topology golden fixtures pass |

---

# 32. Definition of Done

- Phase-1 A00–A14/A16 are implemented with Registry/version metadata; A15 is implemented only at the Phase-5 release gate;
- every recommendation-relevant metric has source/formula lineage;
- bounded SQL verified against pinned Databricks schemas;
- no fabricated CPU/memory utilization;
- when Phase 5 is active, A15 multi-warehouse evidence remains internal to O6 contract semantics;
- component tests pass on pandas Phase-1 backend;
- contracts ready for pandas↔PySpark parity testing in Phase 2.
