"""
Deterministic triage. No model call.

Two independent computations per repo:
  - bucket: mutually exclusive, by push age measured against the snapshot's
    captured_at (not wall clock, so results are reproducible).
  - has_deployment_evidence: an orthogonal boolean. The signal this project
    exists to find is "quiet AND has deployment evidence"; that pairing only
    survives if deployment is a flag, not a bucket.

Buckets, assigned in priority order:
  1. insufficient-evidence  pushed_at missing or null
  2. recently-active        <= 90 days
  3. quiet                  91-365 days
  4. long-quiet             > 365 days
"""

from datetime import datetime, timezone

from estate import load_snapshot

RECENT_MAX_DAYS = 90
QUIET_MAX_DAYS = 365

# Deploy-config filenames. These are keys in each repo's `files` dict; the
# VALUE (not the key's presence) indicates whether the file exists.
DEPLOY_FILES = [
    "Dockerfile",
    "vercel.json",
    "netlify.toml",
    "amplify.yml",
    "template.yaml",
    "serverless.yml",
    "docker-compose.yml",
]


def _parse_dt(value):
    """Parse an ISO 8601 timestamp (handles trailing 'Z'). None if unparseable."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def has_deployment_evidence(repo):
    """True if any deploy config file is present, or any workflow exists."""
    files = repo.get("files", {})
    if any(files.get(name) for name in DEPLOY_FILES):
        return True
    return bool(repo.get("workflows"))


def _age_days(repo, captured_at):
    """Days between pushed_at and the snapshot capture time. None if no pushed_at."""
    pushed = _parse_dt(repo.get("pushed_at"))
    if pushed is None or captured_at is None:
        return None
    return (captured_at - pushed).days


def classify(repo, captured_at):
    """Return (bucket, has_deployment_evidence, reason) for one repo."""
    deploy = has_deployment_evidence(repo)
    deploy_note = "; deployment evidence present" if deploy else ""

    age = _age_days(repo, captured_at)
    if age is None:
        return "insufficient-evidence", deploy, "no pushed_at date available" + deploy_note
    if age <= RECENT_MAX_DAYS:
        bucket = "recently-active"
    elif age <= QUIET_MAX_DAYS:
        bucket = "quiet"
    else:
        bucket = "long-quiet"
    return bucket, deploy, f"pushed {age} days before capture{deploy_note}"


def triage(snapshot):
    """Return a list of records: full_name, bucket, has_deployment_evidence, reason."""
    captured_at = _parse_dt(snapshot.get("captured_at"))
    records = []
    for repo in snapshot.get("repos", []):
        bucket, deploy, reason = classify(repo, captured_at)
        records.append(
            {
                "full_name": repo.get("full_name"),
                "bucket": bucket,
                "has_deployment_evidence": deploy,
                "reason": reason,
            }
        )
    return records


def print_table(records, repo_count):
    """Print the triage table, per-bucket counts, and the total."""
    name_w = max((len(r["full_name"] or "") for r in records), default=20)
    name_w = max(name_w, len("full_name"))
    bucket_w = len("insufficient-evidence")

    header = f"{'full_name':<{name_w}}  {'bucket':<{bucket_w}}  {'deploy':<6}  reason"
    print(header)
    print("-" * len(header))
    for r in records:
        deploy = "yes" if r["has_deployment_evidence"] else "no"
        print(
            f"{(r['full_name'] or ''):<{name_w}}  "
            f"{r['bucket']:<{bucket_w}}  "
            f"{deploy:<6}  "
            f"{r['reason']}"
        )

    print("-" * len(header))
    counts = {}
    for r in records:
        counts[r["bucket"]] = counts.get(r["bucket"], 0) + 1
    for bucket in ("insufficient-evidence", "recently-active", "quiet", "long-quiet"):
        print(f"  {bucket:<{bucket_w}}  {counts.get(bucket, 0)}")
    total = sum(counts.values())
    print(f"  {'TOTAL':<{bucket_w}}  {total}  (snapshot repo_count: {repo_count})")


def main():
    snapshot = load_snapshot()
    records = triage(snapshot)
    print_table(records, snapshot.get("repo_count"))


if __name__ == "__main__":
    main()
