# Testing and Review Strategy

## Pyramid by change type

| Change | Required first/primary test |
|---|---|
| pure deterministic function | unit test, then component |
| Analyzer formula/signal/blocker | unit + contract + Golden |
| Optimizer candidate/eligibility | unit + component + Golden |
| Estimator money | cent-exact unit + property/invariant + Golden |
| Decision comparator | deterministic unit + Golden |
| DecisionContext/hash | canonicalization/property/parity |
| Capability Registry | manifest/schema/dependency/architecture |
| repository/Delta | contract + round-trip + idempotency |
| DAB | bundle validate + dependency/migration + deployed integration |
| statistical model | fixed reference fixture + uncertainty/OOD tests |
| ML | chronological eval + calibration/OOD/drift + fallback |
| LLM | JSON/schema + hard scorer + adversarial + grounded eval |
| lifecycle | state transition + integration + realization Golden |

## TDD rule

Use RED → GREEN → REFACTOR when a behavior can be expressed before implementation.

Do not force ceremonial TDD around:
- trivial configuration wiring;
- generated files;
- exploratory external connectivity.

For those, define the acceptance check before the edit and run it immediately afterward.

## E2E

E2E must exercise the release from its real entry point to its externally observable result.

Examples:
- CLI/source read → Analyzer → Optimizer → Decision → Recommendation;
- DAB job → Delta migration → pipeline tasks → Gold output;
- agent packet → structured result → Review Adapter → persisted review state.

Mocks may support the E2E but cannot be the only proof for a release whose exit gate requires live DAB/source behavior.

## `/code-review low`

Invoke explicitly after green pre-review tests.

Current Claude Code supports effort-level code review; `low` intentionally trades breadth for high-confidence findings.

Block completion on:
- correctness bugs;
- spec/architecture violations;
- data corruption/financial errors;
- unsafe migrations;
- security/privacy issues;
- missing tests for changed material behavior.

Nits that do not affect correctness may be recorded without blocking unless REVIEW.md says otherwise.
