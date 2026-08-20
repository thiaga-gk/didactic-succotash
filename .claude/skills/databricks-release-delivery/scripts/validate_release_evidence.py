#!/usr/bin/env python3
from pathlib import Path
import argparse, json, sys

REQUIRED_TOP = [
    "release_id","status","artifact_baseline","git","dependencies","tests",
    "code_review","e2e","source_e2e","financial_evidence","merge",
    "known_limitations","rollback_or_migration_notes"
]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("evidence")
    args=ap.parse_args()
    p=Path(args.evidence)
    obj=json.loads(p.read_text(encoding="utf-8"))
    errors=[]

    for k in REQUIRED_TOP:
        if k not in obj:
            errors.append(f"missing top-level field: {k}")

    if obj.get("status") in {"READY_TO_MERGE","COMPLETE"}:
        deps=obj.get("dependencies",{})
        if not deps.get("all_complete",False):
            errors.append("merge-ready/complete requires dependencies.all_complete=true")

        git=obj.get("git",{})
        if git.get("base_branch")!="develop":
            errors.append("git.base_branch must be develop")
        expected_branch=f"release/{obj.get('release_id')}"
        if git.get("release_branch")!=expected_branch:
            errors.append(f"git.release_branch must be {expected_branch}")
        for k in ["base_sha","worktree_path","validated_against_develop_sha","tested_head_sha"]:
            if not git.get(k):
                errors.append(f"merge-ready/complete requires git.{k}")

        tests=obj.get("tests",[])
        if not tests:
            errors.append("merge-ready/complete requires at least one test record")
        for i,t in enumerate(tests):
            if "command" not in t or "exit_code" not in t or "class" not in t:
                errors.append(f"test[{i}] missing command/class/exit_code")
            elif t.get("required",True) and t["exit_code"] != 0:
                errors.append(f"required test[{i}] failed: {t.get('command')}")

        cr=obj.get("code_review",{})
        if cr.get("command") != "/code-review low":
            errors.append("requires code_review.command exactly '/code-review low'")
        if cr.get("blocking_findings_open") != 0:
            errors.append("requires zero open blocking code-review findings")

        e2e=obj.get("e2e",{})
        if e2e.get("result")!="PASS":
            errors.append("requires e2e.result=PASS")

        se=obj.get("source_e2e",{})
        if se.get("mode")!="REAL_SOURCE_SYSTEM":
            errors.append("requires source_e2e.mode=REAL_SOURCE_SYSTEM")
        if se.get("mock_only") is not False:
            errors.append("requires source_e2e.mock_only=false")
        if se.get("result")!="PASS" or se.get("exit_code")!=0:
            errors.append("requires passing source-system E2E")
        if not se.get("source_systems"):
            errors.append("requires source_e2e.source_systems")
        if se.get("tested_head_sha") != git.get("tested_head_sha"):
            errors.append("source_e2e.tested_head_sha must equal git.tested_head_sha")

        fin=obj.get("financial_evidence",{})
        if fin.get("aws_cost_basis")=="PRICE_REGISTRY_ESTIMATE":
            if fin.get("aws_actual_available") is not False:
                errors.append("PRICE_REGISTRY_ESTIMATE requires aws_actual_available=false")
            if not fin.get("price_registry_version") or not fin.get("price_registry_sha256"):
                errors.append("price-registry basis requires version and SHA-256 provenance")

        base=obj.get("artifact_baseline",{})
        for k in ["prd","hla","release_plan","golden_catalog"]:
            if not base.get(k):
                errors.append(f"requires artifact_baseline.{k}")

    if obj.get("status")=="COMPLETE":
        merge=obj.get("merge",{})
        if not merge.get("verified_in_develop",False):
            errors.append("COMPLETE requires merge.verified_in_develop=true")
        if merge.get("merged_head_sha") != obj.get("git",{}).get("tested_head_sha"):
            errors.append("COMPLETE requires develop to contain the exact tested head SHA")

    print(f"Evidence: {p}")
    print(f"Errors: {len(errors)}")
    for e in errors:
        print(f"ERROR: {e}")
    sys.exit(1 if errors else 0)

if __name__=="__main__":
    main()
