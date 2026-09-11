"""
snapshot_estate.py
Pre-hackathon data prep for Observator Clew. Allowed under the rules: this is
data collection, not agent logic. Disclose it in the README as pre-existing tooling.

Usage:
    export GITHUB_TOKEN=ghp_...        # public_repo read scope is enough
    python snapshot_estate.py           # writes estate-snapshot.json

What it collects per repo (all deterministic facts, nothing interpreted):
    name, description, pushed_at, created_at, archived, fork, language,
    homepage, topics, open_issues_count, default_branch, html_url,
    stargazers_count, size_kb, has_pages,
    files: presence of key deploy/config files
    workflows: list of workflow filenames under .github/workflows/
"""

import json
import os
import sys
import time
from datetime import datetime, timezone

import requests

USER = "earlgreyhot1701D"
API = "https://api.github.com"


def load_dotenv(path=".env"):
    """Minimal .env loader so the token can live in a gitignored file."""
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


load_dotenv()
TOKEN = os.environ.get("GITHUB_TOKEN")
HEADERS = {"Accept": "application/vnd.github+json"}
if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"

# Files whose presence is evidence. Presence only; contents are Saturday's job.
KEY_FILES = [
    "README.md",
    "LICENSE",
    "Dockerfile",
    "vercel.json",
    "netlify.toml",
    "amplify.yml",
    "template.yaml",       # AWS SAM
    "serverless.yml",
    "package.json",
    "requirements.txt",
    "pyproject.toml",
    ".env.example",
    "docker-compose.yml",
]


def get(url, params=None):
    for attempt in range(3):
        r = requests.get(url, headers=HEADERS, params=params, timeout=30)
        if r.status_code == 403 and "rate limit" in r.text.lower():
            reset = int(r.headers.get("X-RateLimit-Reset", time.time() + 60))
            wait = max(reset - int(time.time()), 5)
            print(f"rate limited, sleeping {wait}s", file=sys.stderr)
            time.sleep(wait)
            continue
        return r
    return r


def list_repos():
    repos, page = [], 1
    while True:
        r = get(f"{API}/users/{USER}/repos",
                params={"per_page": 100, "page": page, "type": "owner", "sort": "pushed"})
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        repos.extend(batch)
        page += 1
    return repos


def file_presence(full_name, branch):
    """One call per repo: the root tree. Cheaper than one call per file."""
    r = get(f"{API}/repos/{full_name}/git/trees/{branch}")
    if r.status_code != 200:
        return {f: None for f in KEY_FILES}, None  # None = unknown, not False
    names = {item["path"] for item in r.json().get("tree", [])}
    return {f: (f in names) for f in KEY_FILES}, names


def workflows(full_name):
    r = get(f"{API}/repos/{full_name}/contents/.github/workflows")
    if r.status_code != 200:
        return []
    return [item["name"] for item in r.json() if item.get("type") == "file"]


def main():
    if not TOKEN:
        print("No GITHUB_TOKEN set. Unauthenticated limit is 60 calls/hour; "
              "this script needs ~3 per repo. Set the token.", file=sys.stderr)
    raw = list_repos()
    print(f"{len(raw)} repos found", file=sys.stderr)

    snapshot = {
        "owner": USER,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "repo_count": len(raw),
        "repos": [],
    }

    for i, r in enumerate(raw, 1):
        full = r["full_name"]
        branch = r.get("default_branch") or "main"
        files, _ = file_presence(full, branch)
        wf = workflows(full)
        snapshot["repos"].append({
            "name": r["name"],
            "full_name": full,
            "html_url": r["html_url"],
            "description": r.get("description"),
            "created_at": r["created_at"],
            "pushed_at": r["pushed_at"],
            "archived": r["archived"],
            "fork": r["fork"],
            "language": r.get("language"),
            "homepage": r.get("homepage") or None,
            "topics": r.get("topics", []),
            "open_issues_count": r["open_issues_count"],
            "stargazers_count": r["stargazers_count"],
            "size_kb": r["size"],
            "has_pages": r.get("has_pages", False),
            "default_branch": branch,
            "files": files,
            "workflows": wf,
        })
        print(f"[{i}/{len(raw)}] {r['name']}", file=sys.stderr)

    with open("estate-snapshot.json", "w") as f:
        json.dump(snapshot, f, indent=2)
    print("wrote estate-snapshot.json", file=sys.stderr)


if __name__ == "__main__":
    main()
