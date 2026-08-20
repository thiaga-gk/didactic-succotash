# Databricks Primary-Source Verification — 2026-08-14

This audit revalidated the SQL Warehouse source hierarchy and Phase-2 DAB assumptions against current first-party documentation.

| Design fact | Verified source | Result |
|---|---|---|
| SQLWH core configuration history | https://docs.databricks.com/aws/en/admin/system-tables/warehouses | `system.compute.warehouses` exposes warehouse type/channel/size/min/max/auto-stop/tags/change history; use before redundant API reads |
| SQLWH state/scale events | https://docs.databricks.com/aws/en/admin/system-tables/warehouse-events | `system.compute.warehouse_events` records start/stop/run/scale events |
| Query workload/performance history | https://docs.databricks.com/aws/en/admin/system-tables/query-history | `system.query.history` is account/regional query evidence and is currently Public Preview |
| Databricks usage/cost | https://docs.databricks.com/aws/en/admin/system-tables/billing | `system.billing.usage` is the primary billable-usage source |
| Published pricing | https://docs.databricks.com/aws/en/admin/system-tables/pricing | `system.billing.list_prices` is historical published pricing, not a substitute for negotiated enterprise rates |
| Warehouse-level statement timeout | https://docs.databricks.com/aws/en/sql/language-manual/parameters/statement_timeout | warehouse-level timeout is Beta and API-only; retain Policy/capability gate |
| DAB project/deployment model | https://docs.databricks.com/aws/en/dev-tools/bundles/ | DAB is source-controlled IaC/CI-CD for project resources |
| DAB job task graph | https://docs.databricks.com/aws/en/dev-tools/bundles/job-task-types | bundle job definitions support task dependencies; v2 uses a hard schema-migration-before-consumers DAG |
| System-table schema evolution | https://docs.databricks.com/aws/en/admin/system-tables/ | additive columns/struct fields may appear; use explicit projections and schema-version tolerance |

## Normative conclusion

For SQL Warehouse analysis:

```text
system tables first
→ deterministic derived metrics
→ product-owned derived state
→ Databricks API only for unresolved/API-only fields or authorized apply-time operations
→ AWS/enterprise sources for evidence Databricks does not own
```

This conclusion is now explicit across Analyzer, Runtime, Data/DAB, Diagnostic, Index, Release and Golden artifacts.
