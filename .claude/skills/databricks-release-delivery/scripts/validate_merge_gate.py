#!/usr/bin/env python3
from pathlib import Path
import argparse, subprocess, json, sys

def run(args,cwd,check=True):
    p=subprocess.run(args,cwd=cwd,text=True,capture_output=True)
    if check and p.returncode:
        raise RuntimeError(f"$ {' '.join(args)}\n{p.stdout}{p.stderr}")
    return p

def git(repo,*args,check=True):
    return run(["git",*args],repo,check)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",default=".")
    ap.add_argument("--evidence",required=True)
    args=ap.parse_args()

    repo=Path(git(Path(args.repo).resolve(),"rev-parse","--show-toplevel").stdout.strip())
    evp=Path(args.evidence)
    if not evp.is_absolute():
        evp=repo/evp
    ev=json.loads(evp.read_text())
    errors=[]

    rid=ev.get("release_id")
    branch=git(repo,"branch","--show-current").stdout.strip()
    head=git(repo,"rev-parse","HEAD").stdout.strip()

    if ev.get("status") not in {"READY_TO_MERGE","COMPLETE"}:
        errors.append("status must be READY_TO_MERGE or COMPLETE")
    if ev.get("git",{}).get("base_branch")!="develop":
        errors.append("git.base_branch must be develop")
    if branch != f"release/{rid}":
        errors.append(f"current branch must be release/{rid}, found {branch}")
    if ev.get("git",{}).get("release_branch") != branch:
        errors.append("evidence release_branch does not match current branch")
    if git(repo,"status","--porcelain").stdout.strip():
        errors.append("release worktree must be clean before merge gate")

    # Latest develop ref.
    remotes=git(repo,"remote").stdout.split()
    if "origin" in remotes:
        git(repo,"fetch","origin","develop")
        latest=git(repo,"rev-parse","origin/develop").stdout.strip()
    else:
        latest=git(repo,"rev-parse","develop").stdout.strip()

    if ev.get("git",{}).get("validated_against_develop_sha") != latest:
        errors.append("develop advanced or evidence lacks validated_against_develop_sha; rebase/retest required")

    if ev.get("git",{}).get("tested_head_sha") != head:
        errors.append("git.tested_head_sha does not equal current release HEAD")

    for i,test in enumerate(ev.get("tests",[])):
        if test.get("required",True) and test.get("exit_code") != 0:
            errors.append(f"required test[{i}] did not pass")

    cr=ev.get("code_review",{})
    if cr.get("command")!="/code-review low":
        errors.append("code_review.command must be /code-review low")
    if cr.get("blocking_findings_open") != 0:
        errors.append("blocking code-review findings remain")

    e2e=ev.get("source_e2e",{})
    if e2e.get("mode")!="REAL_SOURCE_SYSTEM":
        errors.append("source_e2e.mode must be REAL_SOURCE_SYSTEM")
    if e2e.get("mock_only") is not False:
        errors.append("source_e2e.mock_only must be false")
    if e2e.get("result")!="PASS" or e2e.get("exit_code")!=0:
        errors.append("real source-system E2E did not pass")
    if e2e.get("tested_head_sha") != head:
        errors.append("source_e2e.tested_head_sha does not equal current release HEAD")
    if not e2e.get("source_systems"):
        errors.append("source_e2e.source_systems must identify real sources/endpoints")

    print(f"Release: {rid}")
    print(f"HEAD: {head}")
    print(f"Latest develop: {latest}")
    print(f"Errors: {len(errors)}")
    for e in errors:
        print("ERROR:",e)
    sys.exit(1 if errors else 0)

if __name__=="__main__":
    main()
