# Release Completion Gate

Release evidence is stored outside the Git worktree (default sibling delivery-evidence directory or CI artifact store). This keeps the certified worktree clean and preserves evidence after worktree deletion.

## Required evidence

```yaml
release_id: P1-Rxx
status: COMPLETE
artifact_baseline:
  prd: ...
  hla: ...
  adrs: [...]
  tsds: [...]
  release_plan: ...
  golden_catalog: ...
git:
  base_sha: ...
  head_sha: ...
dependencies:
  all_complete: true
tests:
  - command: ...
    class: unit|contract|component|integration|architecture|golden|e2e|dab
    exit_code: 0
code_review:
  command: /code-review low
  blocking_findings_open: 0
e2e:
  type: golden|release-specific|live-dab
  result: PASS
known_limitations: []
rollback_or_migration_notes: ...
completed_at_utc: ...
```

## Hard failures

Status cannot be `COMPLETE` if:
- any required test did not run;
- an E2E requirement is satisfied only by a unit test;
- `/code-review low` has unresolved blocking findings;
- artifact versions are unknown;
- a required migration was not exercised;
- a live-environment gate was claimed from mocks;
- the change introduces future-release scope.
