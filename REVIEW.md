# Code Review Instructions

Review only newly introduced or changed behavior.

Treat these as **blocking/important** findings:

- violation of PRD/HLA/ADR/TSD authority;
- Kernel/SQLWH pack duplication or dependency inversion;
- skipped applicable Analyzer/Optimizer;
- unsupported telemetry or API use when the approved system-table source resolves the field;
- incorrect Decimal/cost/savings logic or double counting;
- DecisionContext/hash/reevaluation errors;
- missing idempotency or unsafe Delta migration;
- DAB task dependency or rollback defect;
- LLM authority leakage, tool leakage in Phase 3, fabricated evidence/config/money;
- security/privacy/credential exposure;
- missing regression test for changed material behavior;
- claiming E2E/live behavior that was only mocked;
- merging a release whose source-system E2E is not bound to the exact final HEAD or latest `develop`;
- price-registry AWS estimates labeled as CUR/invoice actual or realized savings;
- Bronze duplication of Databricks system tables without an approved reason.

Nits should be limited to issues that materially improve maintainability. Do not churn code for style already enforced by formatter/linter.
