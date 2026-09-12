"""
The two guards, kept as visible code the model cannot reach.

  persistence_guard  runs BEFORE the model. A candidate the human already
                     declined, whose evidence fingerprint is unchanged, is
                     dropped without a model call. Human decisions outrank
                     model judgment.
  policy_guard       runs AFTER the model. The model recommends SURFACE or
                     SUPPRESS; whether that actually interrupts the human is
                     this deterministic step, named rather than inlined.

Decisions live in state/decisions.json, written by the Telegram buttons and
read here on the next run. This is the memory layer across runs.
"""

import json
import os
from datetime import datetime, timezone

DECISIONS_PATH = "state/decisions.json"

# Deploy-config filenames whose presence forms part of the fingerprint. Same
# set the triage deployment flag uses; tested by value, not key membership.
DEPLOY_FILES = [
    "Dockerfile",
    "vercel.json",
    "netlify.toml",
    "amplify.yml",
    "template.yaml",
    "serverless.yml",
    "docker-compose.yml",
]


def _load_decisions():
    if not os.path.exists(DECISIONS_PATH):
        return {}
    with open(DECISIONS_PATH, encoding="utf-8") as f:
        return json.load(f)


def _save_decisions(decisions):
    os.makedirs(os.path.dirname(DECISIONS_PATH), exist_ok=True)
    with open(DECISIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(decisions, f, indent=2)


def evidence_fingerprint(repo_record):
    """The facts that, if unchanged, mean a prior decision still applies."""
    files = repo_record.get("files", {})
    present = sorted(name for name in DEPLOY_FILES if files.get(name))
    return {
        "pushed_at": repo_record.get("pushed_at"),
        "archived": repo_record.get("archived"),
        "open_issues_count": repo_record.get("open_issues_count"),
        "deploy_files": present,
    }


def record_decision(repo, decision, repo_record):
    """
    Persist a human decision keyed by full_name. decision is 'investigate' or
    'no_action'. Stores the evidence fingerprint so the persistence guard can
    tell later whether anything materially changed.
    """
    decisions = _load_decisions()
    decisions[repo] = {
        "repo": repo,
        "decision": decision,
        "decided_at": datetime.now(timezone.utc).isoformat(),
        "evidence_fingerprint": evidence_fingerprint(repo_record),
    }
    _save_decisions(decisions)
    return decisions[repo]


def persistence_guard(candidates, snapshot):
    """
    Return (to_investigate, auto_suppressed_notes).

    A candidate is auto-suppressed (and never sent to the model) when a stored
    no_action decision exists for it AND the freshly recomputed fingerprint
    matches the stored one. Everything else is kept.
    """
    decisions = _load_decisions()
    by_full = {r.get("full_name"): r for r in snapshot.get("repos", [])}

    to_investigate = []
    auto_suppressed_notes = []
    for cand in candidates:
        full = cand.get("full_name")
        stored = decisions.get(full)
        if stored and stored.get("decision") == "no_action":
            current = evidence_fingerprint(by_full.get(full, {}))
            if current == stored.get("evidence_fingerprint"):
                decided_date = (stored.get("decided_at") or "")[:10]
                auto_suppressed_notes.append(
                    f"{full}: No action, {decided_date} (evidence unchanged)"
                )
                continue
        to_investigate.append(cand)

    return to_investigate, auto_suppressed_notes


def policy_guard(findings):
    """
    The model-recommendation -> actual-interruption boundary, made visible.
    Only SURFACE findings reach the human.
    """
    return [f for f in findings if f.recommendation == "SURFACE"]


def clear_decisions():
    """
    Demo tooling: empty the decision store and return how many were cleared.
    Touches state/decisions.json only. Does not affect runs, snapshot, or state
    other than the decisions themselves.
    """
    count = len(_load_decisions())
    _save_decisions({})
    return count
