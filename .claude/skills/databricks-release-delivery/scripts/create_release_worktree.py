#!/usr/bin/env python3
from pathlib import Path
import argparse, subprocess, sys, json, re

def run(args, cwd, check=True):
    p=subprocess.run(args,cwd=cwd,text=True,capture_output=True)
    if check and p.returncode:
        raise RuntimeError(f"$ {' '.join(args)}\n{p.stdout}{p.stderr}")
    return p

def git(repo,*args,check=True):
    return run(["git",*args],repo,check)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",default=".")
    ap.add_argument("--release",required=True)
    ap.add_argument("--worktree-root")
    args=ap.parse_args()

    release=args.release.upper()
    if not re.fullmatch(r"P\d+-R\d{2}",release):
        raise SystemExit("release must look like P1-R01")

    repo=Path(git(Path(args.repo).resolve(),"rev-parse","--show-toplevel").stdout.strip())
    branch=git(repo,"branch","--show-current").stdout.strip()
    if branch!="develop":
        raise SystemExit(f"primary checkout must be on develop, found {branch!r}")

    if git(repo,"status","--porcelain").stdout.strip():
        raise SystemExit("primary develop checkout is not clean")

    remotes=git(repo,"remote").stdout.split()
    if "origin" in remotes:
        git(repo,"fetch","origin","develop")
        # Require fast-forward only; never rewrite local develop.
        git(repo,"merge","--ff-only","origin/develop")

    base_sha=git(repo,"rev-parse","HEAD").stdout.strip()
    release_branch=f"release/{release}"

    branch_exists=git(repo,"show-ref","--verify",f"refs/heads/{release_branch}",check=False).returncode==0

    wt_root=Path(args.worktree_root).resolve() if args.worktree_root else repo.parent/f"{repo.name}-worktrees"
    wt=wt_root/release
    wt_root.mkdir(parents=True,exist_ok=True)

    evidence_root=repo.parent/f"{repo.name}-delivery-evidence"
    evidence_dir=evidence_root/release
    evidence_dir.mkdir(parents=True,exist_ok=True)

    if wt.exists():
        raise SystemExit(f"worktree path already exists: {wt}")

    if branch_exists:
        git(repo,"worktree","add",str(wt),release_branch)
        mode="CONTINUE_EXISTING_BRANCH"
    else:
        git(repo,"worktree","add","-b",release_branch,str(wt),base_sha)
        mode="CREATED"

    result={
        "release_id":release,
        "base_branch":"develop",
        "base_sha":base_sha,
        "release_branch":release_branch,
        "worktree_path":str(wt),
        "evidence_dir":str(evidence_dir),
        "mode":mode,
    }
    print(json.dumps(result,indent=2))

if __name__=="__main__":
    main()
