# Release Workflow State Machine

```text
NOT_STARTED
  ↓
CONTEXT_RESOLVED
  ↓
PREFLIGHT_PASSED
  ↓
PLAN_WRITTEN
  ↓
TESTS_RED_OR_ACCEPTANCE_DEFINED
  ↓
IMPLEMENTED
  ↓
LOCAL_VERIFIED
  ↓
CODE_REVIEWED
  ↓
E2E_VERIFIED
  ↓
COMPLETE
```

Any stage can transition to `BLOCKED` or `FAILED`.

## Idempotency

Re-running delivery for the same release:
- read existing release evidence;
- detect completed/partial steps;
- rerun verification if code/artifacts changed;
- never blindly recreate or duplicate migrations/capability registrations.

## Dependency rule

A release may consume interfaces from a completed prior release. It may not assume implementation from a future release.

## Fix loop

```text
test/review/e2e finding
  → classify root cause
  → add/strengthen regression test
  → fix
  → rerun narrow tests
  → rerun affected broad tests
  → rerun code review if material
```
