#!/usr/bin/env python3
from pathlib import Path
import json, re, sys

ROOT=Path(__file__).resolve().parents[4]
SKILL=ROOT/".claude/skills/databricks-release-delivery"
errors=[]

claude=ROOT/"CLAUDE.md"
if not claude.exists():
    errors.append("missing CLAUDE.md")
else:
    text=claude.read_text()
    lines=len(text.splitlines())
    if lines >= 200:
        errors.append(f"CLAUDE.md should stay under 200 lines; found {lines}")
    for token in [
        "databricks-release-delivery",
        "/code-review low",
        "Same `authoritative_context_hash`",
        "zero callable agent tools",
        "No `COMPLETE_WITH_SKIPPED_TESTS`",
        "release/<release-id>",
        "PRICE_REGISTRY_ESTIMATE",
    ]:
        if token not in text:
            errors.append(f"CLAUDE.md missing {token!r}")

skill=SKILL/"SKILL.md"
if not skill.exists():
    errors.append("missing delivery SKILL.md")
else:
    text=skill.read_text()
    if len(text.splitlines()) >= 500:
        errors.append("delivery SKILL.md should remain under 500 lines")
    if not re.match(r"^---\n.*?name:\s*databricks-release-delivery.*?\n---",text,re.S):
        errors.append("invalid skill frontmatter")
    for token in [
        "resolve_release.py",
        "TDD",
        "/code-review low",
        "release-evidence.json",
        "COMPLETE_WITH_SKIPPED_TESTS",
        "release-specific E2E",
        "REAL_SOURCE_SYSTEM",
        "validate_merge_gate.py",
        "create_release_worktree.py",
    ]:
        if token not in text:
            errors.append(f"SKILL.md missing {token!r}")

for ref in ["artifact-precedence.md","release-workflow.md","testing-and-review.md","git-worktree-and-merge.md","financial-evidence-fallback.md","completion-gate.md"]:
    if not (SKILL/"references"/ref).exists():
        errors.append(f"missing reference {ref}")

for s in ["resolve_release.py","create_release_worktree.py","validate_release_evidence.py","validate_merge_gate.py"]:
    if not (SKILL/"scripts"/s).exists():
        errors.append(f"missing script {s}")

try:
    obj=json.loads((SKILL/"evals/evals.json").read_text())
    if obj.get("skill_name")!="databricks-release-delivery" or len(obj.get("evals",[]))!=4:
        errors.append("invalid eval set")
except Exception as e:
    errors.append(f"invalid eval JSON: {e}")

print(f"Errors: {len(errors)}")
for e in errors:
    print("ERROR:",e)
sys.exit(1 if errors else 0)
