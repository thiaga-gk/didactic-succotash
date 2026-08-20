# Git Worktree and Merge Gate

Every Product Release uses a separate Git worktree and branch.

## Branch/worktree contract

```text
base branch: develop
release branch: release/P1-R08
worktree: sibling worktree directory
```

Creation sequence:

```text
clean primary checkout on develop
→ fetch origin/develop if configured
→ ff-only update develop
→ create release/<release-id> from that SHA
→ create separate worktree
```

Never implement directly on `develop`.

## Final-tested-commit invariant

The release must be fully committed before the merge E2E.

```text
release HEAD = H
real source-system E2E tests H
code review covers H/diff
latest develop used for final validation = D
```

Merge is eligible only while `develop == D`.

If develop advances:
1. rebase `release/<id>` onto latest develop;
2. resolve conflicts in the release worktree;
3. rerun impacted tests;
4. rerun `/code-review low` if material;
5. rerun real source-system E2E;
6. record the new tested HEAD.

## Why fast-forward is preferred

`git merge --ff-only release/<id>` makes develop point to the exact release commit that passed real source-system E2E. No untested merge tree is introduced.

If branch protection requires a PR, CI must bind evidence to the exact source commit and must reject a merge strategy that produces an untested tree unless the post-merge tree is retested.

## Worktree cleanup

After verified merge:

```bash
git worktree remove <worktree>
git branch -d release/<id>
git worktree prune
```

Never delete a worktree/branch before merge evidence is preserved in the external evidence directory/CI artifact store.

## Source E2E requirement

Mock-only E2E never permits merge.

The evidence must identify:
- environment;
- real Databricks source tables/endpoints;
- real DAB job/run/query identifiers when available;
- command and exit code;
- tested Git SHA;
- log/artifact refs;
- `mock_only=false`.

A simple connectivity probe is sufficient only for a release whose exit gate is connectivity. Later releases must execute their actual release behavior against those sources.
