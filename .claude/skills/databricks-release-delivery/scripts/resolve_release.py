#!/usr/bin/env python3
from pathlib import Path
import argparse, re, sys, json

def version_tuple(path: Path):
    m=re.search(r"_v(\d+)\.(\d+)\.(\d+)\.md$", path.name)
    return tuple(int(x) for x in m.groups()) if m else (-1,-1,-1)

def find_one(repo: Path, pattern: str) -> Path:
    matches=sorted(repo.rglob(pattern))
    if not matches:
        raise FileNotFoundError(f"Could not find {pattern} under {repo}")
    # Highest semantic artifact version wins; shortest path breaks ties.
    matches.sort(key=lambda p: (version_tuple(p), tuple(-x for x in [len(p.parts)]), str(p)), reverse=True)
    return matches[0]

def parse_table_row(line: str):
    return [x.strip() for x in line.strip("|").split("|")]

def semver_tuple(v: str):
    return tuple(int(x) for x in v.split("."))

def expand_component_releases(component_text: str, tsd_files):
    declared=set()
    for f in tsd_files:
        declared.update(re.findall(r"REL-[A-Z]+-\d+\.\d+\.\d+", f.read_text(encoding="utf-8", errors="ignore")))

    result=set(re.findall(r"REL-[A-Z]+-\d+\.\d+\.\d+", component_text))

    # Expand shorthand ranges such as `REL-ANA-0.2.0` → `0.3.0`.
    for m in re.finditer(r"REL-([A-Z]+)-(\d+\.\d+\.\d+)[^;\n]*?→\s*`?(\d+\.\d+\.\d+)`?", component_text):
        comp,start,end=m.groups()
        prefix=f"REL-{comp}-"
        lo,hi=semver_tuple(start),semver_tuple(end)
        for rid in declared:
            if rid.startswith(prefix):
                v=semver_tuple(rid[len(prefix):])
                if lo <= v <= hi:
                    result.add(rid)
    return sorted(result)

def expand_golden_refs(text: str, golden_lines):
    ids=set(re.findall(r"GT-\d{3}", text))

    # GT-019..027
    for a,b in re.findall(r"GT-(\d{3})\.\.(\d{3})", text):
        ids.update(f"GT-{n:03d}" for n in range(int(a), int(b)+1))

    # GT-003/004/007/008: reuse the first GT prefix for shorthand numbers.
    for m in re.finditer(r"GT-(\d{3}(?:/\d{3})+)", text):
        ids.update(f"GT-{part}" for part in m.group(1).split("/"))

    # Phase-N `GT-*` means all Golden rows whose phase column is Phase N.
    phase_m=re.search(r"Phase-(\d+)\s*`GT-\*`", text)
    if phase_m:
        phase=phase_m.group(1)
        for line in golden_lines:
            if line.startswith("| GT-"):
                c=parse_table_row(line)
                if len(c) >= 2 and re.search(rf"\bPhase\s+{phase}\b", c[1]):
                    ids.add(c[0])
    return sorted(ids)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--release", required=True)
    ap.add_argument("--out")
    args=ap.parse_args()

    repo=Path(args.repo).resolve()
    release_id=args.release.upper()

    release_file=find_one(repo, "*product_release_plan_v*.md")
    golden_file=find_one(repo, "*golden_e2e_test_scenarios_v*.md")
    prd_file=find_one(repo, "*product_prd_v*.md")
    hla_file=find_one(repo, "*high_level_architecture_v*.md")
    tsd_files=sorted(repo.rglob("*technical-spec*.md")) + sorted(repo.rglob("TS-*.md"))
    tsd_files=list(dict.fromkeys(tsd_files))
    adr_files=sorted(repo.rglob("ADR-*.md"))

    release_row=None
    for line in release_file.read_text(encoding="utf-8").splitlines():
        if line.startswith(f"| `{release_id}`"):
            c=parse_table_row(line)
            if len(c)!=10:
                raise ValueError(f"Unexpected release-plan shape for {release_id}: {len(c)} columns")
            release_row={
                "release_id":c[0].strip("`"),
                "phase":c[1],
                "build_order":c[2],
                "outcome":c[3],
                "component_releases":c[4],
                "runtime":c[5],
                "intelligence":c[6],
                "dependencies":c[7],
                "exit_gate":c[8],
                "traceability":c[9],
            }
            break
    if not release_row:
        raise KeyError(f"{release_id} not found in {release_file}")

    gold_lines=golden_file.read_text(encoding="utf-8").splitlines()
    rel_ids=expand_component_releases(release_row["component_releases"]+" "+release_row["traceability"], tsd_files)
    gt_ids=expand_golden_refs(release_row["exit_gate"]+" "+release_row["traceability"], gold_lines)

    rel_to_tsds={}
    for rid in rel_ids:
        hits=[]
        for f in tsd_files:
            if f.exists() and rid in f.read_text(encoding="utf-8", errors="ignore"):
                hits.append(str(f.relative_to(repo)))
        rel_to_tsds[rid]=hits

    golden_rows={}
    for gid in gt_ids:
        hit=next((x for x in gold_lines if x.startswith(f"| {gid} |")),None)
        golden_rows[gid]=hit

    # ADRs with phase/component language are candidates; implementation must narrow manually.
    phase=release_row["phase"]
    adr_candidates=[]
    keywords=set(re.findall(r"\b(?:Policy|Analyzer|Estimator|Tier|Modeler|Optimizer|Orchestrator|Decision|Recommendation|Lifecycle|Registry|Context|LLM|Diagnostic|topology|DAB|Delta|ML)\b",
                            " ".join(release_row.values()), re.I))
    for f in adr_files:
        text=f.read_text(encoding="utf-8",errors="ignore")
        if any(re.search(rf"\b{re.escape(k)}\b",text,re.I) for k in keywords):
            adr_candidates.append(str(f.relative_to(repo)))

    unresolved=[rid for rid,hits in rel_to_tsds.items() if not hits]
    direct_golden=bool(gt_ids)

    md=[
        f"# Release Context — {release_id}",
        "",
        f"**Phase:** {release_row['phase']}  ",
        f"**Build order:** {release_row['build_order']}  ",
        "",
        "## Product Release row",
        "",
        f"- **Outcome:** {release_row['outcome']}",
        f"- **Component releases:** {release_row['component_releases']}",
        f"- **Runtime:** {release_row['runtime']}",
        f"- **Intelligence:** {release_row['intelligence']}",
        f"- **Dependencies:** {release_row['dependencies']}",
        f"- **Exit gate:** {release_row['exit_gate']}",
        f"- **Traceability:** {release_row['traceability']}",
        "",
        "## Authoritative artifacts",
        "",
        f"- PRD: `{prd_file.relative_to(repo)}`",
        f"- HLA: `{hla_file.relative_to(repo)}`",
        f"- Product Release Plan: `{release_file.relative_to(repo)}`",
        f"- Golden catalog: `{golden_file.relative_to(repo)}`",
        "",
        "## Component release → TSD resolution",
        "",
    ]
    if rel_ids:
        for rid in rel_ids:
            hits=rel_to_tsds[rid]
            md.append(f"- `{rid}` → "+(", ".join(f"`{x}`" for x in hits) if hits else "**UNRESOLVED**"))
    else:
        md.append("- No exact component `REL-*` identifier in this row; resolve component TSDs from traceability/outcome before implementation.")

    md += ["","## Direct Golden references",""]
    if gt_ids:
        for gid in gt_ids:
            md.append(f"- `{gid}` — {'FOUND' if golden_rows[gid] else 'MISSING'}")
    else:
        md += [
            "- None in the Product Release row.",
            "- **Delivery requirement:** create a release-specific E2E test from the exit gate/TSD contract; do not renumber the approved Golden catalog."
        ]

    md += ["","## Candidate ADRs — verify relevance",""]
    if adr_candidates:
        md += [f"- `{x}`" for x in adr_candidates]
    else:
        md.append("- No candidate ADRs found by keyword scan; inspect ADR index manually.")

    md += ["","## Preflight status",""]
    md.append(f"- Exact component release IDs unresolved: **{len(unresolved)}**")
    md.append(f"- Direct Golden coverage in release row: **{'YES' if direct_golden else 'NO — release-specific E2E required'}**")
    md.append("- PRD requirement resolution: **MANUAL/TSD TRACEABILITY REQUIRED BEFORE CODING**")
    md.append("- Dependency completion: **VERIFY FROM `execution/releases/*/release-evidence.json`**")
    md.append("- Environment/source prerequisites: **VERIFY**")

    result="\n".join(md)+"\n"
    if args.out:
        p=Path(args.out)
        if not p.is_absolute(): p=repo/p
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(result,encoding="utf-8")
        print(p)
    else:
        print(result)

    if unresolved:
        sys.exit(2)

if __name__=="__main__":
    main()
