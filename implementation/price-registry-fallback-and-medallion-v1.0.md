# AWS Price Registry Fallback + DAB Medallion Implementation Profile

**Status:** Normative implementation profile for v2.0.1  
**Scope:** SQL Warehouse pack while AWS CUR/Data Exports are unavailable

## 1. Financial source precedence

```text
Databricks actual usage
  → system.billing.usage

Databricks effective rate
  → enterprise/invoice rate if available
  → system.billing.list_prices fallback

AWS customer-cloud economics
  → CUR/Data Exports actual/effective evidence when available
  → source-controlled AWS price registry estimate while CUR is unavailable
  → DBX-only result when Policy permits and registry evidence is insufficient
```

The price registry is **not** an actual billing ledger.

Required labels:

```text
aws_cost_basis = PRICE_REGISTRY_ESTIMATE
aws_actual_available = false
total_cost_quality = MIXED_ACTUAL_ESTIMATED
```

Do not populate actual AWS realized/cash/commitment fields from the registry.

## 2. Source-controlled registry

Canonical source:

`config/pricing/aws_ec2_price_registry.yaml`

Requirements:
- reviewed through Git;
- effective-dated;
- region/resource/purchase-option specific;
- source reference + retrieval timestamp;
- no overlapping effective periods for one lookup key;
- registry version + Git SHA + SHA-256 included in run evidence/DecisionContext;
- missing material keys fail closed or downgrade to DBX-only according to Policy.

On-Demand entries may be refreshed from AWS Price List data.

Spot entries require an explicit time/AZ-aware estimation method. Static On-Demand pricing is not Spot actual.


## 2.1 SQL Warehouse quantity derivation — system tables first

For **classic/pro SQL warehouses**, the AWS registry can be useful even without CUR because current Databricks documentation exposes the infrastructure shape for each warehouse size.

Use:

- `system.compute.warehouses` for effective warehouse size/config history;
- `system.compute.warehouse_events` for start/stop/scale events and `cluster_count`;
- `system.billing.usage` for actual Databricks DBU usage and `warehouse_id`; `usage_metadata.node_type` can be used as a cross-check where populated;
- the reviewed price registry for the relevant AWS rates.

Current documented classic/pro cluster shape:

| Warehouse size | Driver | Workers per cluster | Worker instance |
|---|---|---:|---|
| 2X-Small | `i3.2xlarge` | 1 | `i3.2xlarge` |
| X-Small | `i3.2xlarge` | 2 | `i3.2xlarge` |
| Small | `i3.4xlarge` | 4 | `i3.2xlarge` |
| Medium | `i3.8xlarge` | 8 | `i3.2xlarge` |
| Large | `i3.8xlarge` | 16 | `i3.2xlarge` |
| X-Large | `i3.16xlarge` | 32 | `i3.2xlarge` |
| 2X-Large | `i3.16xlarge` | 64 | `i3.2xlarge` |
| 3X-Large | `i3.16xlarge` | 128 | `i3.2xlarge` |
| 4X-Large | `i3.16xlarge` | 256 | `i3.2xlarge` |
| 5X-Large | `i3.16xlarge` | 512 | `i3.2xlarge` |

The sizing map is a versioned platform capability/source contract and must be revalidated at implementation/release time because Databricks notes it can vary with product/region/workspace availability. 5X-Large is currently a Preview-dependent size.

For each effective event interval:

```text
cluster_hours = interval_hours × cluster_count

estimated_ec2_cost_interval
  = cluster_hours
  × (
      effective_driver_hourly_rate(size, region)
      + worker_count(size) × effective_worker_hourly_rate(region)
    )
```

Integrate over all event/config intervals in the observation period.

If Spot is enabled, apply Spot pricing only to the node categories proven by the supported SQL Warehouse Spot-policy contract. Never assume a driver/worker purchase-option split.

### Coverage label

The initial registry estimate is normally:

```text
aws_estimate_coverage = EC2_CORE_ONLY
```

unless the implementation also has evidence-backed EBS/network/other quantity models and rates.

Therefore:

```text
MIXED_ACTUAL_ESTIMATED + EC2_CORE_ONLY
```

must not be presented as a fully reconciled AWS total.

**Serverless SQL Warehouse:** do not apply this customer EC2 registry model. Serverless infrastructure is Databricks-managed; use Databricks billing evidence and only separately attributable customer AWS costs if explicitly proven.

## 3. Transition to CUR

When CUR/Data Exports becomes available:
- enable the CUR adapter;
- CUR/actual evidence takes precedence;
- retain historical registry snapshots for reproducibility;
- context financial digest changes;
- Estimator/Decision reevaluate the affected financial path;
- do not rerun unrelated workload Analyzers solely because pricing evidence changed.

## 4. DAB medallion model

Yes: the Phase-2 DAB data model is medallion-based.

```text
Databricks system tables ───────────────┐
(query in place)                        │
                                       ▼
External sources → BRONZE → SILVER → GOLD
                   │          │         │
                   │          │         └ recommendation / lifecycle / realized value
                   │          └ canonical config/evidence/model/optimizer/PlanState/financial facts
                   └ CUR / AWS price-registry snapshot / commercial-rate normalization

CONTROL = Policy / Registry / DecisionContext / source manifests
ML      = feature / model / evaluation lineage
```

We deliberately do **not** copy Databricks system tables wholesale into Bronze. They remain governed first-party sources queried in place. Product-owned canonical facts derived from them live in Silver.

## 5. Release delivery implication

P1-R04/P1-R06 may proceed without CUR only when:
- price registry has complete material lookup coverage;
- registry provenance validates;
- outputs are labeled estimated;
- source-system E2E uses real Databricks system tables and the real registry lookup;
- merge gate passes on the exact final Git HEAD.
