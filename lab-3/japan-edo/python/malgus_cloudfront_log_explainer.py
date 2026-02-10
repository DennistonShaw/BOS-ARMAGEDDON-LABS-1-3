#!/usr/bin/env python3
"""
malgus_cloudfront_log_explainer.py

Script 2 — Edge Proof (CloudFront)

Summarizes CloudFront cache outcomes (Hit / Miss / RefreshHit)
from CloudFront *standard logs* stored in S3 and writes:

  ./lab3-audit-pack/02_edge-proof-cloudfront.txt

Key improvements:
- Uses boto3 (no AWS CLI dependency).
- If --bucket is wrong / doesn't exist, it writes a helpful proof file:
  - lists buckets visible in the account
  - suggests likely CloudFront log buckets/prefixes
  - explains next steps to complete the edge proof

Requirements:
- Python 3.8+
- boto3: pip3 install boto3
- AWS credentials configured (same as AWS CLI)
"""

from __future__ import annotations

import argparse
import gzip
import io
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

# ---------- OUTPUT LOCATION ----------
AUDIT_DIR = Path(__file__).parent / "lab3-audit-pack"
OUTPUT_FILE = AUDIT_DIR / "02_edge-proof-cloudfront.txt"
# -----------------------------------

TARGETS = {"Hit", "Miss", "RefreshHit"}


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def s3():
    return boto3.client("s3")


def list_buckets() -> List[str]:
    resp = s3().list_buckets()
    return sorted([b["Name"] for b in resp.get("Buckets", [])])


def bucket_exists(bucket: str) -> bool:
    try:
        s3().head_bucket(Bucket=bucket)
        return True
    except ClientError:
        return False


def list_objects(bucket: str, prefix: str, max_keys: int = 2000) -> List[Dict]:
    """
    Returns object dicts with Key/LastModified/Size for up to max_keys objects.
    """
    client = s3()
    paginator = client.get_paginator("list_objects_v2")
    out: List[Dict] = []
    kwargs = {"Bucket": bucket, "Prefix": prefix} if prefix else {"Bucket": bucket}
    for page in paginator.paginate(**kwargs):
        for obj in page.get("Contents", [])[:]:
            out.append(obj)
            if len(out) >= max_keys:
                return out
    return out


def choose_latest_objects(objs: List[Dict], n: int) -> List[Dict]:
    return sorted(objs, key=lambda o: o.get("LastModified"), reverse=True)[:n]


def get_object_bytes(bucket: str, key: str) -> bytes:
    resp = s3().get_object(Bucket=bucket, Key=key)
    return resp["Body"].read()


def iter_lines_from_object(key: str, raw: bytes) -> Iterable[str]:
    """
    CloudFront standard logs are often gzipped (.gz) but sometimes plain text.
    """
    if key.endswith(".gz"):
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as gz:
            text = gz.read().decode("utf-8", errors="replace")
            for line in text.splitlines():
                yield line
    else:
        text = raw.decode("utf-8", errors="replace")
        for line in text.splitlines():
            yield line


def parse_cloudfront_standard_logs(keys_and_bytes: List[Tuple[str, bytes]]) -> Dict[str, int]:
    counts = Counter()
    other = Counter()

    for key, raw in keys_and_bytes:
        field_index: Optional[Dict[str, int]] = None

        for line in iter_lines_from_object(key, raw):
            if line.startswith("#Fields:"):
                fields = line.split(":", 1)[1].strip().split()
                field_index = {name: idx for idx, name in enumerate(fields)}
                continue

            if not line or line.startswith("#"):
                continue

            if not field_index:
                other["(missing_fields_header)"] += 1
                continue

            parts = line.split("\t")

            def get_field(name: str) -> str:
                idx = field_index.get(name)
                if idx is None or idx >= len(parts):
                    return ""
                return parts[idx]

            outcome = get_field("x-edge-result-type") or get_field("x-edge-response-result-type")

            if not outcome:
                other["(missing_outcome)"] += 1
            elif outcome in TARGETS:
                counts[outcome] += 1
            else:
                other[outcome] += 1

    for k, v in other.items():
        counts[f"Other:{k}"] += v

    return dict(counts)


def likely_cloudfront_log_bucket_names(buckets: List[str]) -> List[str]:
    """
    Heuristic only: CloudFront log buckets often contain these substrings.
    """
    hints = ("cloudfront", "cf-", "cdn", "logs", "log")
    cand = [b for b in buckets if any(h in b.lower() for h in hints)]
    return cand[:20]


def write_proof(
    *,
    generated_utc: str,
    bucket: Optional[str],
    prefix: str,
    analyzed_keys: List[str],
    counts: Optional[Dict[str, int]],
    error: Optional[str],
    bucket_inventory: Optional[List[str]],
    candidates: Optional[List[str]],
) -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("02 — EDGE PROOF (CLOUDFRONT)\n")
        f.write("===========================\n\n")
        f.write(f"Generated (UTC): {generated_utc}\n")
        f.write("Evidence source: CloudFront Standard Logs (S3)\n")
        f.write("Goal: Demonstrate edge caching behavior via x-edge-result-type outcomes (Hit/Miss/RefreshHit)\n\n")

        f.write("INPUT\n")
        f.write("-----\n")
        f.write(f"Bucket: {bucket or '-'}\n")
        f.write(f"Prefix: {prefix or '(none)'}\n\n")

        if error:
            f.write("STATUS\n")
            f.write("------\n")
            f.write("❌ FAILED TO READ LOGS\n")
            f.write(f"Reason: {error}\n\n")

            if bucket_inventory is not None:
                f.write("BUCKETS VISIBLE IN THIS ACCOUNT\n")
                f.write("-------------------------------\n")
                if bucket_inventory:
                    for b in bucket_inventory[:50]:
                        f.write(f"- {b}\n")
                else:
                    f.write("- (none returned)\n")
                f.write("\n")

            if candidates is not None:
                f.write("LIKELY CLOUDFRONT LOG BUCKET CANDIDATES (HEURISTIC)\n")
                f.write("---------------------------------------------------\n")
                if candidates:
                    for b in candidates:
                        f.write(f"- {b}\n")
                else:
                    f.write("- (no obvious candidates)\n")
                f.write("\n")

            f.write("NEXT STEPS\n")
            f.write("----------\n")
            f.write("1) Confirm the correct S3 bucket name where CloudFront standard logs are delivered.\n")
            f.write("2) Re-run this script with: --bucket <correct_bucket> [--prefix <logs_prefix>]\n")
            f.write("3) Once logs are readable, this proof will include Hit/Miss/RefreshHit counts.\n")
            return

        # Success path
        f.write("ANALYZED OBJECTS\n")
        f.write("---------------\n")
        for k in analyzed_keys:
            f.write(f"- {k}\n")
        f.write("\n")

        f.write("CACHE OUTCOME SUMMARY\n")
        f.write("---------------------\n")
        counts = counts or {}
        hit = counts.get("Hit", 0)
        miss = counts.get("Miss", 0)
        rhit = counts.get("RefreshHit", 0)
        total_core = hit + miss + rhit

        def pct(n: int, d: int) -> str:
            return "0.0%" if d == 0 else f"{(n * 100.0 / d):.1f}%"

        f.write(f"Hit       : {hit} ({pct(hit, total_core)})\n")
        f.write(f"Miss      : {miss} ({pct(miss, total_core)})\n")
        f.write(f"RefreshHit: {rhit} ({pct(rhit, total_core)})\n\n")

        # Show a few other outcomes if present
        others = {k: v for k, v in counts.items() if k not in ("Hit", "Miss", "RefreshHit")}
        if others:
            f.write("OTHER OUTCOMES (TOP)\n")
            f.write("--------------------\n")
            for k, v in sorted(others.items(), key=lambda x: (-x[1], x[0]))[:20]:
                f.write(f"{k}: {v}\n")
            f.write("\n")

        f.write("INTERPRETATION (AUDIT / OPS)\n")
        f.write("-----------------------------\n")
        f.write("- Hit: served from CloudFront edge cache (edge delivery evidence)\n")
        f.write("- Miss: forwarded to origin (edge cache did not contain object)\n")
        f.write("- RefreshHit: cached object revalidated with origin\n")
        f.write("- This demonstrates edge-layer request handling distinct from origin processing.\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate CloudFront edge proof from standard logs in S3.")
    ap.add_argument("--bucket", default="", help="S3 bucket containing CloudFront standard logs")
    ap.add_argument("--prefix", default="", help="Optional S3 prefix for logs (folder path)")
    ap.add_argument("--latest", type=int, default=3, help="Analyze latest N log objects (default: 3)")
    ap.add_argument("--max-scan", type=int, default=2000, help="Max objects to scan to find latest (default: 2000)")
    args = ap.parse_args()

    # Credential sanity
    try:
        boto3.client("sts").get_caller_identity()
    except NoCredentialsError:
        write_proof(
            generated_utc=utc_stamp(),
            bucket=args.bucket or None,
            prefix=args.prefix,
            analyzed_keys=[],
            counts=None,
            error="AWS credentials not found (NoCredentialsError). Run `aws sts get-caller-identity` first.",
            bucket_inventory=None,
            candidates=None,
        )
        print(f"Proof file written to: {OUTPUT_FILE}")
        return 2
    except ClientError as e:
        write_proof(
            generated_utc=utc_stamp(),
            bucket=args.bucket or None,
            prefix=args.prefix,
            analyzed_keys=[],
            counts=None,
            error=f"AWS credential/API error: {e}",
            bucket_inventory=None,
            candidates=None,
        )
        print(f"Proof file written to: {OUTPUT_FILE}")
        return 2

    # If bucket not provided, try to guide the user by listing buckets/candidates
    buckets = list_buckets()
    candidates = likely_cloudfront_log_bucket_names(buckets)

    if not args.bucket:
        write_proof(
            generated_utc=utc_stamp(),
            bucket=None,
            prefix=args.prefix,
            analyzed_keys=[],
            counts=None,
            error="No bucket provided. CloudFront standard logs must be read from S3.",
            bucket_inventory=buckets,
            candidates=candidates,
        )
        print(f"Proof file written to: {OUTPUT_FILE}")
        return 2

    # Validate bucket exists/accessible
    if not bucket_exists(args.bucket):
        write_proof(
            generated_utc=utc_stamp(),
            bucket=args.bucket,
            prefix=args.prefix,
            analyzed_keys=[],
            counts=None,
            error=f"NoSuchBucket or not accessible: '{args.bucket}'",
            bucket_inventory=buckets,
            candidates=candidates,
        )
        print(f"Proof file written to: {OUTPUT_FILE}")
        return 2

    # List objects and pick latest
    try:
        objs = list_objects(args.bucket, args.prefix, max_keys=max(1, args.max_scan))
    except ClientError as e:
        write_proof(
            generated_utc=utc_stamp(),
            bucket=args.bucket,
            prefix=args.prefix,
            analyzed_keys=[],
            counts=None,
            error=f"Failed listing objects in s3://{args.bucket}/{args.prefix}: {e}",
            bucket_inventory=buckets,
            candidates=candidates,
        )
        print(f"Proof file written to: {OUTPUT_FILE}")
        return 2

    if not objs:
        write_proof(
            generated_utc=utc_stamp(),
            bucket=args.bucket,
            prefix=args.prefix,
            analyzed_keys=[],
            counts=None,
            error=f"No objects found under s3://{args.bucket}/{args.prefix or '(root)'}",
            bucket_inventory=buckets,
            candidates=candidates,
        )
        print(f"Proof file written to: {OUTPUT_FILE}")
        return 2

    latest = choose_latest_objects(objs, max(1, args.latest))

    # Download and analyze
    keys_and_bytes: List[Tuple[str, bytes]] = []
    analyzed_keys: List[str] = []
    try:
        for o in latest:
            key = o["Key"]
            analyzed_keys.append(key)
            raw = get_object_bytes(args.bucket, key)
            keys_and_bytes.append((key, raw))
    except ClientError as e:
        write_proof(
            generated_utc=utc_stamp(),
            bucket=args.bucket,
            prefix=args.prefix,
            analyzed_keys=analyzed_keys,
            counts=None,
            error=f"Failed downloading one or more log objects: {e}",
            bucket_inventory=buckets,
            candidates=candidates,
        )
        print(f"Proof file written to: {OUTPUT_FILE}")
        return 2

    counts = parse_cloudfront_standard_logs(keys_and_bytes)

    write_proof(
        generated_utc=utc_stamp(),
        bucket=args.bucket,
        prefix=args.prefix,
        analyzed_keys=analyzed_keys,
        counts=counts,
        error=None,
        bucket_inventory=None,
        candidates=None,
    )

    print(f"Proof file written to: {OUTPUT_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
