#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import argparse, hashlib, json, sys

import yaml
from jsonschema import Draft202012Validator, FormatChecker

def dt(v):
    if v is None:
        return None
    s=v.replace("Z","+00:00")
    x=datetime.fromisoformat(s)
    if x.tzinfo is None:
        x=x.replace(tzinfo=timezone.utc)
    return x.astimezone(timezone.utc)

def key(e):
    return (
        e.get("cloud"), e.get("service"), e.get("region"),
        e.get("availability_zone"), e.get("resource_type"),
        e.get("instance_type"), e.get("operating_system"),
        e.get("tenancy"), e.get("purchase_option"),
        e.get("currency"), e.get("unit")
    )

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--registry",default="config/pricing/aws_ec2_price_registry.yaml")
    ap.add_argument("--schema",default="config/pricing/aws_ec2_price_registry.schema.json")
    ap.add_argument("--require-entries",action="store_true")
    args=ap.parse_args()

    reg_path=Path(args.registry)
    schema_path=Path(args.schema)
    raw=reg_path.read_bytes()
    obj=yaml.safe_load(raw)
    schema=json.loads(schema_path.read_text())

    errors=[]
    v=Draft202012Validator(schema,format_checker=FormatChecker())
    for e in sorted(v.iter_errors(obj),key=lambda x:list(x.path)):
        errors.append(f"schema {list(e.path)}: {e.message}")

    entries=(obj or {}).get("entries",[])
    if args.require_entries and not entries:
        errors.append("registry has no entries")

    by_key={}
    for i,e in enumerate(entries):
        try:
            if Decimal(e["price"]) < 0:
                errors.append(f"entry[{i}] negative price")
        except (InvalidOperation,KeyError):
            pass

        try:
            start=dt(e["effective_start_utc"])
            end=dt(e.get("effective_end_utc"))
            if end is not None and end <= start:
                errors.append(f"entry[{i}] effective_end_utc must be after start")
        except Exception as exc:
            errors.append(f"entry[{i}] invalid effective date: {exc}")
            continue

        if e.get("purchase_option")=="SPOT":
            if not e.get("estimation_method"):
                errors.append(f"entry[{i}] SPOT requires estimation_method")
            if not e.get("observation_start_utc") or not e.get("observation_end_utc"):
                errors.append(f"entry[{i}] SPOT requires observation window")

        by_key.setdefault(key(e),[]).append((start,end,i))

    # Effective-period overlap check.
    for k,periods in by_key.items():
        periods.sort(key=lambda x:x[0])
        for prev,curr in zip(periods,periods[1:]):
            p_start,p_end,p_i=prev
            c_start,c_end,c_i=curr
            if p_end is None or c_start < p_end:
                errors.append(f"entries[{p_i},{c_i}] overlap for key {k}")

    digest=hashlib.sha256(raw).hexdigest()
    print(f"registry_version: {(obj or {}).get('registry_version')}")
    print(f"entries: {len(entries)}")
    print(f"sha256: {digest}")
    print(f"errors: {len(errors)}")
    for e in errors:
        print("ERROR:",e)

    sys.exit(1 if errors else 0)

if __name__=="__main__":
    main()
