# Financial Evidence Fallback — AWS Price Registry Until CUR Exists

AWS CUR/Data Exports remains the preferred source for actual attributable customer-cloud AWS economics.

If CUR is not available, the implementation may use a **source-controlled, effective-dated AWS price registry** to produce planning estimates.

## Precedence

```text
AWS CUR/Data Exports attributable actual/effective cost
    ↓
approved invoice/chargeback evidence if available
    ↓
source-controlled AWS price registry estimate
    ↓
DBX-only result if Policy permits
    ↓
BLOCKED if total-cost evidence is mandatory
```

## Registry requirements

A price entry must include at least:

```yaml
cloud: AWS
service: EC2
region: us-east-2
instance_type: m6i.xlarge
operating_system: Linux
tenancy: Shared
purchase_option: ON_DEMAND
currency: USD
unit: HOUR
price: "0.19200000"
effective_start_utc: "2026-08-01T00:00:00Z"
effective_end_utc: null
source_type: AWS_PRICE_LIST
source_reference: ...
source_retrieved_at_utc: ...
```

For Spot, static On-Demand price is not a Spot actual. Use an explicitly versioned Spot estimation method and evidence window, for example approved `DescribeSpotPriceHistory` observations. Label it estimated.

## Financial labels

Registry-based outputs must carry:

```text
aws_cost_basis = PRICE_REGISTRY_ESTIMATE
aws_actual_available = false
cost_quality = MIXED_ACTUAL_ESTIMATED | ESTIMATED
```

Do not report registry-derived AWS cost as:
- CUR actual;
- invoice actual;
- realized AWS cash saving;
- commitment freed actual.

Databricks usage can still be actual from `system.billing.usage`; the total must visibly distinguish actual Databricks cost from estimated AWS cost.

## Realization

Until CUR/actual AWS evidence exists:

```text
Databricks realized value = may be actual when reconciled
AWS realized value        = unavailable / estimated only
Total realized actual     = unavailable if AWS is material
```

A planning run-rate may be shown separately.

When CUR becomes available, switch the adapter/basis by Policy and preserve the historical registry snapshot for reproducibility.

## Source control and refresh

Recommended repo structure:

```text
config/pricing/
├── aws_ec2_price_registry.yaml
└── aws_ec2_price_registry.schema.json
```

Refresh by a reviewed PR. A maintenance script may seed/update On-Demand entries from the official AWS Price List APIs. Spot estimates may be refreshed from `DescribeSpotPriceHistory`. Runtime optimization should not depend on those public pricing APIs if the reviewed registry is the configured source.

Record file Git SHA + SHA-256 digest in run/source evidence.
