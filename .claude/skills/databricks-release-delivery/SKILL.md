---
name: databricks-release-delivery
description: Deliver one approved Databricks Compute Optimization product release end to end from PRD, HLA, ADRs, TSDs, Product Release Plan, and Golden E2E scenarios. Use whenever asked to implement, continue, finish, verify, review, merge, or release any P1-Rxx through P6-Rxx item, or to deliver a whole phase sequentially. Creates a dedicated Git worktree/`release/<release-id>` branch from freshly synchronized `develop`, builds a release context, applies test-first implementation where appropriate, runs required tests and real source-system E2E on the exact final commit, invokes `/code-review low`, fixes findings, and permits fast-forward merge to `develop` only when the evidence gate passes.
---

# Databricks Release Delivery

Deliver against the approved artifacts; do not redesign the product while coding.

## Required inputs

Locate these from the repo; do not ask the user to paste them if present:

- PRD v2.0.0
- HLA v2.0.0
- relevant ADRs
- `tech-specs/`
- SQL Warehouse Product Release Plan v2.0.0
- Golden E2E catalog v2.0.0
- repo `CLAUDE.md`
- prior release evidence
- current code/tests/DAB resources

Read `references/artifact-precedence.md`, `release-workflow.md`,
`testing-and-review.md`, `git-worktree-and-merge.md`,
`financial-evidence-fallback.md`, and `completion-gate.md`.

## Invocation modes

### One release — default

```text
deliver P1-R08
continue P2-R04
finish P3-R07
```

Implement exactly one Product Release row. Do not start the next release automatically.

### Whole phase — explicit only

```text
deliver phase 1
```

Execute releases in Product Release Plan build order. A release must pass its completion gate before the next begins. Stop immediately on a blocker or failed gate.

## 0. Create the release worktree — mandatory

Never implement a Product Release directly on `develop`.

From a clean primary checkout:

```bash
python .claude/skills/databricks-release-delivery/scripts/create_release_worktree.py \
  --repo . --release <P#-R##>
```

The helper:

1. requires the primary checkout to be on clean `develop`;
2. fetches `origin/develop` when a remote is available;
3. fast-forwards local `develop` only—never force-resets it;
4. creates `release/<release-id>` from the synchronized `develop` SHA;
5. creates a separate sibling worktree;
6. prints the worktree path/base SHA for evidence.

Run every subsequent coding/test/review command inside that release worktree.

Record:

```text
base_branch = develop
base_sha
release_branch = release/<release-id>
worktree_path
evidence_dir
```

Set `RELEASE_EVIDENCE_DIR` to the helper's sibling evidence directory. Delivery evidence lives **outside Git/worktrees** so it cannot dirty the commit being certified and it survives worktree cleanup. CI may archive the same directory as a release artifact.

If the release branch/worktree already exists, inspect and continue it; do not create a duplicate.

## 1. Resolve the release

Run:

```bash
python .claude/skills/databricks-release-delivery/scripts/resolve_release.py \
  --repo . --release <P#-R##> --out execution/releases/<release>/release-context.md
```

Then verify the generated context manually against the source artifacts.

The context MUST identify:

- Product Release row/outcome/order/phase;
- dependencies;
- component `REL-*` releases;
- relevant TSD files;
- referenced Golden scenarios;
- exit gate;
- HLA/ADR constraints;
- unresolved source/policy/environment prerequisites.

If an exact PRD requirement is not explicitly mapped in the release row/TSD, infer it from the authoritative component TSD traceability and record the inference. Never invent a requirement.

## 2. Preflight

Fail closed if:

- prior Product Release dependencies are incomplete;
- source artifact versions differ from the approved baseline without an accepted superseding decision;
- the required capability/TSD is not approved for the phase;
- a material `DECISION_REQUIRED` remains;
- required environment access cannot be validated;
- current working tree is not the dedicated `release/<release-id>` worktree;
- the release branch is not descended from synchronized `develop`;
- an implementation would violate Kernel/Pack boundaries;
- Phase 6 is requested without its separately approved detailed TSD/security/evaluation package.

Record preflight in `release-evidence.json`.

## 3. Make a small implementation plan

Write `$RELEASE_EVIDENCE_DIR/implementation-plan.md`.

Plan only this release. Include:

- files/modules to add/change;
- Kernel vs SQLWH Pack placement;
- contracts/schema changes;
- tests to write first;
- DAB/Delta changes;
- expected Golden/E2E paths;
- migration/backward-compatibility concerns.

Do not expand release scope.

## 4. TDD / test first where behavior is testable

Use the test strategy in `references/testing-and-review.md`.

Default:

```text
behavior/bug/business rule        → RED test first
contract/schema                   → contract test first
migration/DAB dependency          → migration/deployment test first
deterministic algorithm           → unit/golden test first
statistical/model behavior        → reference/evaluation fixture first
ML                                → evaluation/admission test before promotion
LLM                               → schema/hard-scorer/adversarial eval first
pure wiring/trivial generated code→ test immediately after wiring if RED adds no value
```

Do not pretend a test was written first if it was not.

## 5. Implement the minimum release scope

Rules:

- Kernel implements shared mechanics once.
- SQLWH-specific logic lives under `packs/sql_warehouse/`.
- one `(capability_id, semantic_version)` → one executable implementation;
- all phase/applicability-valid registered Analyzers/Optimizers execute;
- T1–T4 changes bounded depth, not capability applicability;
- Modeler predicts; Estimator owns money;
- LLM does not author config/money/lifecycle;
- same authoritative context hash → no authoritative recomputation;
- system tables first; APIs only for unresolved/API-only fields/actions;
- when AWS CUR/Data Exports are unavailable, a source-controlled effective-dated AWS price registry may provide **planning-estimate** economics only; mark the basis `PRICE_REGISTRY_ESTIMATE` and never present it as actual/realized AWS cost;
- Phase-2 data follows Control + Bronze/Silver/Gold + ML: system tables query in place, Bronze holds external/raw-normalized evidence, Silver canonical facts/results, Gold recommendation/lifecycle/value;
- no next-release code unless required for an explicit backward-compatible interface stub.

## 6. Verify incrementally

After each coherent slice run the narrowest relevant tests.

Before review, all required release-local checks must pass:

```text
format/lint/type
unit
contract/schema
component
integration
architecture/import-boundary
migration/DAB validation if touched
targeted Golden
```

Use the repo's actual commands. Never fabricate passing output.

## 7. Run `/code-review low`

After implementation tests are green, explicitly invoke the current Claude Code built-in:

```text
/code-review low
```

Do not create a project skill named `code-review`; it can override the bundled skill.

Treat every high-confidence correctness, architecture, security, data-integrity,
spec-compliance, or test-gap finding as blocking.

For each accepted finding:

```text
finding
→ reproduce/test where possible
→ fix root cause
→ rerun impacted tests
```

Then run `/code-review low` again when the fix materially changes code.

Do not mark complete with unresolved blocking findings.

## 8. Run release E2E against real source systems

Every Product Release requires a **real source-system E2E proof before merge**. Mock-only execution never satisfies this gate.

Before the final E2E:

1. commit all intended release code;
2. fetch the latest `develop`;
3. if `develop` advanced, rebase the release branch onto it;
4. rerun all affected tests and `/code-review low` after material conflict/rebase changes;
5. require a clean worktree;
6. capture `tested_head_sha = git rev-parse HEAD`;
7. run the source-system E2E on that exact SHA.

Minimum real-source evidence by phase:

| Phase | Required real source-system proof |
|---:|---|
| 1 | bounded read-only Databricks system-table queries through the configured SQL Warehouse + real release entry point; AWS price-registry lookup is allowed when CUR is unavailable |
| 2 | `databricks bundle validate`, deploy to dev/test, run affected Lakeflow/DAB tasks against real system tables and product Delta state |
| 3 | Phase-2 source path plus real configured model endpoint for releases that exercise LLM behavior; no tools |
| 4 | real approved SQLWH diagnostic source(s) for releases that consume diagnostics |
| 5 | real multi-warehouse source evidence plus deployed topology workflow for topology releases |
| 6 | blocked until separately approved detailed TSD/security/evaluation package |

If a Product Release row references a Golden, execute it in the required environment.

If it has no direct Golden:
- derive a release-specific E2E from the exit gate/TSD contract;
- add the release test/fixture without silently renumbering the approved Golden catalog.

Evidence MUST record:

```text
mode = REAL_SOURCE_SYSTEM
tested_head_sha
environment
source_systems / tables / endpoints
command
exit_code = 0
Databricks job/run/query IDs where available
artifact/log refs
started_at_utc / completed_at_utc
mock_only = false
```

A connectivity-only query is insufficient once the release implements behavior beyond connectivity; the E2E must exercise the release's real entry point to its externally observable result.


## 9. Release completion evidence

Write outside the Git worktree:

```text
$RELEASE_EVIDENCE_DIR/
├── release-context.md
├── implementation-plan.md
├── release-evidence.json
└── completion-report.md
```

Do not commit this evidence into the release branch. Bind it to the tested Git SHA and archive it through CI/artifact retention.

`release-evidence.json` MUST contain:

- artifact versions/digests;
- base branch=`develop`, synchronized base SHA, release branch and worktree path;
- git final tested head SHA and clean-tree proof;
- changed files;
- dependency status;
- test commands + exit codes;
- Golden/E2E results;
- **real source-system E2E** details including `tested_head_sha`, source tables/endpoints, run/query IDs and `mock_only=false`;
- AWS financial evidence basis (`CUR_ACTUAL`, `PRICE_REGISTRY_ESTIMATE`, `DBX_ONLY`, etc.) when cost is in scope;
- DAB validate/deploy/run IDs when applicable;
- `/code-review low` result and resolved findings;
- known limitations;
- migration/rollback notes;
- completion status.

Allowed completion status:

```text
READY_TO_MERGE
COMPLETE
BLOCKED
FAILED
```

No `COMPLETE_WITH_SKIPPED_TESTS`.

## 10. Merge gate — `develop` receives only the tested commit

After all tests/review/source E2E pass:

```bash
python .claude/skills/databricks-release-delivery/scripts/validate_merge_gate.py \
  --repo . \
  --evidence "$RELEASE_EVIDENCE_DIR/release-evidence.json"
```

The validator fails unless:

- branch is `release/<release-id>`;
- base branch is `develop`;
- working tree is clean;
- latest `develop` SHA equals the develop SHA against which the final release commit was tested;
- all required tests pass;
- `/code-review low` has zero blocking findings;
- E2E is `REAL_SOURCE_SYSTEM`, `mock_only=false`, and PASS;
- E2E `tested_head_sha` equals the current release HEAD.

If `develop` advanced after E2E, **do not merge**. Rebase onto latest `develop` and rerun the affected full verification plus real source-system E2E.

Preferred merge is a **fast-forward** of `develop` to the exact E2E-tested release HEAD:

```bash
git -C <primary-checkout> checkout develop
git -C <primary-checkout> merge --ff-only release/<release-id>
```

This guarantees the merged tree is the exact commit that passed source E2E.

If repository protection requires a PR/remote merge, configure CI to enforce the same tested-head SHA and evidence gate. A merge commit or conflict resolution that changes the tested tree requires new E2E evidence.

After merge:
- verify `develop` contains the tested SHA;
- record merge status/SHA in completion evidence;
- remove the release worktree and delete the local release branch only after the merge is verified.

If permissions prevent merge, status is `READY_TO_MERGE`, not `COMPLETE`.

## 11. Definition of COMPLETE

A release is complete only when:

1. release scope matches the Product Release row;
2. required TSD behavior is implemented;
3. applicable tests pass;
4. targeted Golden/release E2E passes;
5. architecture boundaries pass;
6. `/code-review low` has no unresolved blocking finding;
7. documentation/contracts are updated when implementation changed them;
8. release evidence is complete and reproducible;
9. git diff contains no unrelated next-release work;
10. real source-system E2E passed on the exact final release HEAD;
11. that exact tested HEAD has been merged/fast-forwarded into `develop`.

Report the completed release and stop.

## Phase mode

When explicitly delivering a whole phase:

```text
for release in ProductReleasePlan.phase(build_order):
    deliver(release)
    if release.status != COMPLETE:  # COMPLETE means merged into develop
        STOP
```

At the final phase gate:
- run the phase gate's full Golden/E2E suite;
- create the phase completion report under the external delivery-evidence root;
- do not cross into the next phase unless the user explicitly requested it.

## Never

- mark a release complete because code compiles;
- skip E2E because unit tests passed;
- change PRD/HLA authority to make code easier;
- duplicate Kernel and pack implementations;
- silently skip an applicable Analyzer/Optimizer;
- use REST APIs when an approved system-table source already resolves the analytical field;
- invent unsupported Databricks telemetry;
- let LLM output author authoritative config/money;
- add Phase-6 tools before its detailed approval;
- implement directly on `develop`;
- merge a release whose real source-system E2E did not pass on its exact final HEAD;
- accept mock-only E2E as merge evidence;
- call price-registry-based AWS economics actual or realized;
- continue past a failed release gate.
