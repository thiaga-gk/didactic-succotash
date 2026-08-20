# Implementation Start Here — v2.0.1

1. Read root `CLAUDE.md`.
2. Keep SQL Warehouse as the only implementation-authorized pack.
3. Populate and review `config/pricing/aws_ec2_price_registry.yaml` for required regions/rate keys while CUR is unavailable.
4. Validate it with `python scripts/validate_price_registry.py --require-entries`.
5. Configure read-only Databricks source access for real source-system E2E.
6. Start with `P1-R01`.

Each Product Release:

```text
synchronized develop
→ release/<release-id> worktree
→ implementation/TDD
→ tests
→ /code-review low
→ real source-system E2E on exact final HEAD
→ merge-gate validation
→ ff-only merge into develop
→ evidence archive + worktree cleanup
```

Use:

```text
Use databricks-release-delivery to implement P1-R01.
```

Release evidence is stored outside Git/worktrees so it does not contaminate the SHA being certified.

## AWS CUR not available

That does not block early implementation.

P1-R04/P1-R06 may use the reviewed source-controlled registry for planning estimates. The package must show `PRICE_REGISTRY_ESTIMATE` / `MIXED_ACTUAL_ESTIMATED`; AWS realized actual remains unavailable until CUR or equivalent actual billing evidence exists.

## Phase-2 data model

The DAB model is:

```text
Control
Bronze → Silver → Gold
ML
```

System tables are queried in place. Bronze contains external/raw-normalized evidence such as CUR later, the price-registry snapshot now, and commercial-rate inputs.
