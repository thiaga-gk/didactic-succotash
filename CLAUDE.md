# Databricks Compute Optimization

## Mission

Implement the approved **Databricks Compute Optimization Product v2.0.0** one Product Release at a time. SQL Warehouse is the only implementation-authorized Capability Pack.

## Start every release

Use the `databricks-release-delivery` skill for any `P#-R##` implementation, continuation, verification, or completion.

Authoritative precedence:

1. PRD
2. HLA
3. accepted ADRs / v2 dispositions
4. TSDs
5. Product Release Plan
6. Golden E2E catalog
7. code/tests

If artifacts conflict, stop and report the conflict. Do not resolve it silently in code.

## Architecture invariants

- `kernel/` = shared mechanics/contracts implemented once.
- `packs/sql_warehouse/` = SQLWH-specific capabilities/providers.
- A released `(capability_id, semantic_version)` has exactly one executable implementation.
- Kernel must not statically import concrete SQLWH implementations.
- Packs must not import/call other packs.
- Do not create future compute packs without their approved study/ADRs/TSDs/release/Golden set.

## Authority

- Analyzer: deterministic facts/signals/blockers; never target config.
- Modeler: statistical/ML counterfactuals; expose applicability/uncertainty/fallback.
- Optimizer: bounded concrete technique/config decision; never authoritative money.
- Estimator: authoritative economics/money.
- Orchestrator: capability execution/search/PlanState/reevaluation.
- Decision: final compatible authoritative plan.
- LLM: investigate/challenge/explain only; no config/money/lifecycle authority.
- CapabilityGap: durable and non-executable until normal release.

Every phase/applicability-valid registered Analyzer and Optimizer executes. T1–T4 may bound candidate/model/search depth but may not suppress one.

Same `authoritative_context_hash` => no authoritative recomputation.

## Source priority

For SQLWH analytical evidence:

1. Databricks system tables.
2. Deterministic metrics derived from them.
3. Product-owned derived state.
4. Databricks API only for unresolved/API-only fields or authorized apply-time operations.
5. AWS/enterprise evidence only for facts Databricks does not own.

Until AWS CUR/Data Exports exists, a source-controlled effective-dated AWS price registry is allowed for **planning estimates only**. Label it `PRICE_REGISTRY_ESTIMATE`; never call it actual or realized AWS cost. CUR supersedes it when available.

Phase-2 persistence follows **Control + Bronze → Silver → Gold + ML**. System tables are queried in place; Bronze is for external/raw-normalized evidence such as AWS pricing/CUR/commercial inputs.

Do not duplicate system-table data into Bronze by default. Do not invent unsupported telemetry.

## Phase boundaries

- P1: local/pandas deterministic + statistical SQLWH value proof.
- P2: DAB/Lakeflow + PySpark + managed Delta + governed ML.
- P3: packet-only Intelligence Review; **zero callable agent tools**.
- P4: SQLWH Deep Diagnostic Intelligence; no universal Spark-event assumption.
- P5: A15/M06/O6 topology.
- P6: blocked for implementation until detailed Copilot/tool TSD + security/eval approval.

No next-phase behavior early.

## Git worktree / merge gate

- Every Product Release is implemented in its own worktree on `release/<release-id>`, created from a clean, synchronized `develop`.
- Never implement directly on `develop`.
- Before merge, rebase onto latest `develop` if it advanced; rerun affected verification and **real source-system E2E on the exact final HEAD**.
- Mock-only E2E never permits merge.
- Prefer `git merge --ff-only release/<release-id>` so `develop` receives the exact E2E-tested commit.
- If branch protection requires PR merge, the CI merge gate must bind E2E evidence to the exact tested SHA; an untested merge tree is not acceptable.
- A release is `COMPLETE` only after the tested commit is present in `develop`.

## Delivery rules

- Default: implement one Product Release per invocation.
- Keep diffs scoped to the current release.
- Resolve dependencies before coding.
- Use TDD when behavior is testable: RED -> GREEN -> REFACTOR.
- For schema/DAB changes, write the migration/dependency verification first.
- For ML/LLM, use eval/admission/hard-scorer tests rather than pretending conventional unit TDD is sufficient.
- Never report a test you did not run.
- Do not mark a release complete until its real source-system E2E proof passes and the exact tested commit is merged into `develop`.

After green implementation tests, explicitly run:

`/code-review low`

Fix blocking findings, rerun impacted tests, and rerun review after material fixes.

Do not create a project skill named `code-review`; that can override Claude's bundled command.

## Definition of done

A Product Release is `COMPLETE` only if:

- release scope and required TSD behavior are implemented;
- format/lint/type checks pass where configured;
- required unit/contract/component/integration/architecture tests pass;
- DAB/migration checks pass when touched;
- targeted Golden or release-specific E2E passes;
- `/code-review low` has zero unresolved blocking findings;
- docs/contracts changed by implementation are updated;
- release evidence is written under `execution/releases/<release>/`;
- source E2E is `REAL_SOURCE_SYSTEM`, `mock_only=false`, and bound to the final Git HEAD;
- that exact tested HEAD is merged into `develop`;
- no unrelated future-release code remains in the diff.

No `COMPLETE_WITH_SKIPPED_TESTS`.

## Git / deployment safety

- Release delivery is authorized to merge the evidence-gated release branch into `develop`; do not merge to `main`, tag a release, push protected refs, deploy production, or apply warehouse changes unless separately authorized.
- Human-in-the-loop remains mandatory for production SQL Warehouse configuration changes.
- Never rewrite unrelated user changes.
- Prefer isolated release branches/worktrees when available.

## Quality priorities

Correctness > safety/reliability > financial integrity > deterministic reproducibility > maintainability > performance > convenience.

For cost calculations use Decimal/cent-exact semantics. Independent optimizer savings are not additive. Protective savings remain separate.

## Historical warning

ADR-006's old five-phase sequence is superseded. Retain only its Phase-5 topology deferral. The v2.0.0 six-phase Product Release Plan is current authority.
