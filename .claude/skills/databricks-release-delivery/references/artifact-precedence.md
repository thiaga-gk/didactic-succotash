# Artifact Precedence and Traceability

Use this precedence for implementation conflicts:

1. approved PRD
2. approved HLA
3. accepted ADRs / v2 dispositions
4. component TSDs
5. Product Release Plan
6. Golden E2E catalog
7. implementation code/tests

A lower layer validates/refines a higher layer; it cannot silently redefine it.

## Release context resolution

For the current Product Release:
1. read the exact release row;
2. resolve every exact `REL-*` to the TSD that declares it;
3. read the TSD's upstream traceability and acceptance criteria;
4. identify HLA/ADR invariants that constrain the change;
5. resolve every `GT-*` reference;
6. inspect prior release evidence/dependencies.

If a contradiction exists, stop with `BLOCKED_SPEC_CONFLICT` and report the exact files/sections.

## Historical documents

Do not use superseded historical sequencing as active authority. In v2.0.0, ADR-006's old five-phase sequence is historical; only its Phase-5 topology deferral remains retained.

## Scope control

The active implementation pack is SQL Warehouse. Future compute packs have no implementation authority unless separately approved.
