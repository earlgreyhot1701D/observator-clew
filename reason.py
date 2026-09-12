"""
The agent loop. ReAct, bounded at MAX_TOOL_TURNS = 4, enforced in code.

Runs entirely on /v1/responses (verified Sep 11; Chat Completions cannot do
function tools on this model and there is no fallback). Shape D, verified:
  - responses.create for evidence turns (system prompt + facts in `input` on
    the first call; only function_call_output on chained calls)
  - a final responses.parse(previous_response_id=..., text_format=Finding,
    tools=TOOLS) for the structured finding
  - turns chained with previous_response_id
  - reasoning={"effort": "medium"} is per-call on create
  - client built with timeout=20

The model selects what to investigate and requests evidence; code executes the
fetch; the model observes the real result and only then judges. Do not collapse
this into one pre-fetched call. The round trip is the point.
"""

import json
import os
import sys

from openai import OpenAI
from pydantic import ValidationError

from investigate import fetch_file
from schema import Finding

MAX_TOOL_TURNS = 4
SYSTEM_PROMPT_PATH = "prompts/system_prompt.md"


def load_dotenv(path=".env"):
    """Minimal .env loader, same pattern as the repo's other scripts."""
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

MODEL = os.environ.get("MODEL")

# Flattened tools shape, verified on /v1/responses. No nested "function" key.
TOOLS = [
    {
        "type": "function",
        "name": "fetch_file",
        "description": "Fetch the contents of a file from a GitHub repository.",
        "parameters": {
            "type": "object",
            "properties": {
                "repo": {"type": "string", "description": "owner/name"},
                "path": {"type": "string", "description": "path within the repo"},
            },
            "required": ["repo", "path"],
            "additionalProperties": False,
        },
        "strict": True,
    }
]


def _make_client():
    return OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
        base_url=os.environ.get("OPENAI_BASE_URL") or None,
        timeout=20,
    )


def _load_system_prompt():
    with open(SYSTEM_PROMPT_PATH, encoding="utf-8") as f:
        return f.read()


def _function_calls(response):
    """Return function_call items from a Responses API result."""
    return [
        item
        for item in (getattr(response, "output", []) or [])
        if getattr(item, "type", None) == "function_call"
    ]


def _build_first_input(system_prompt, candidate, repo_record):
    """First call: system prompt, a delimiter, then this candidate's real facts.

    The model must know which files actually exist, or it blind-guesses README.md.
    Facts come from the snapshot record; file presence is tested by value.
    """
    files = repo_record.get("files", {})
    present = [name for name, val in files.items() if val]
    workflows = repo_record.get("workflows", []) or []

    facts_lines = [
        f"repo: {candidate['full_name']}",
        f"bucket: {candidate['bucket']}",
        f"has_deployment_evidence: {candidate['has_deployment_evidence']}",
        f"deterministic_reason: {candidate['reason']}",
        f"files_present: {', '.join(present) if present else '(none)'}",
        f"workflows: {', '.join(workflows) if workflows else '(none)'}",
        f"open_issues_count: {repo_record.get('open_issues_count')}",
        f"archived: {repo_record.get('archived')}",
        f"language: {repo_record.get('language')}",
        f"homepage: {repo_record.get('homepage')}",
        f"has_pages: {repo_record.get('has_pages')}",
        f"topics: {', '.join(repo_record.get('topics', [])) or '(none)'}",
    ]
    facts = "\n".join(facts_lines)
    return (
        f"{system_prompt}\n"
        "\n===== CANDIDATE FACTS (established by code; do not restate differently) =====\n"
        f"{facts}\n"
        "===== END CANDIDATE FACTS =====\n"
        "\nDecide what evidence, if any, you need. Request files with fetch_file, "
        "then produce the finding."
    )


def _run_tool_calls(response, snapshot, checked):
    """Execute each requested fetch_file. Return chained function_call_output items.

    Records every executed fetch into `checked` as (repo, path, "live"|"fallback"),
    so code -- not the model -- owns the what_checked field. Fallback is detected
    by the labeled prefix the fallback string carries.
    """
    outputs = []
    for call in _function_calls(response):
        try:
            args = json.loads(call.arguments)
        except (ValueError, TypeError):
            args = {}
        repo = args.get("repo", "")
        path = args.get("path", "")
        result = fetch_file(repo, path, snapshot)
        mode = "fallback" if result.startswith("[FALLBACK") else "live"
        checked.append((repo, path, mode))
        outputs.append(
            {
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": result,
            }
        )
    return outputs


def _format_what_checked(checked, finding_repo):
    """path (mode) when the fetch repo matches the finding; repo/path (mode) if not.

    Code owns this field, so a cross-repo fetch must never be hidden behind a
    bare path.
    """
    if not checked:
        return ["no additional evidence requested"]
    entries = []
    for repo, path, mode in checked:
        if repo == finding_repo:
            entries.append(f"{path} ({mode})")
        else:
            entries.append(f"{repo}/{path} ({mode})")
    return entries


def _valid_repo_names(snapshot):
    """full_name values only. The decision fingerprint in Block 4 keys on this."""
    return {r["full_name"] for r in snapshot.get("repos", []) if r.get("full_name")}


def _bare_name_index(snapshot):
    """Map bare name -> list of full_names, for normalizing an unambiguous match."""
    index = {}
    for r in snapshot.get("repos", []):
        name = r.get("name")
        full = r.get("full_name")
        if name and full:
            index.setdefault(name, []).append(full)
    return index


def _validate_finding(finding, valid_names, bare_index):
    """Repo must be a full_name; a bare name is normalized only if unambiguous.

    what_cant_know must be substantive. Mutates finding.repo on normalization.
    """
    if finding.repo not in valid_names:
        matches = bare_index.get(finding.repo, [])
        if len(matches) == 1:
            finding.repo = matches[0]
        else:
            return f"cited repo {finding.repo!r} not in snapshot as a full_name"
    bad = {"", "n/a", "na", "none", "nothing", "unknown"}
    if finding.what_cant_know.strip().lower() in bad:
        return "what_cant_know is empty or a placeholder"
    return None


def reason_one(client, candidate, repo_record, snapshot, system_prompt, valid_names, bare_index):
    """
    Run the bounded loop for a single candidate. Returns (Finding, None) on
    success or (None, error_string) on failure. Model failure retries once,
    then the caller drops and logs.

    Code owns what_checked: every executed fetch is recorded here and written
    onto the finding after parsing, overriding whatever the model said.
    """
    checked = []  # (repo, path, "live"|"fallback") for every fetch actually run

    # Turn 1: system prompt + real facts. Model selects and may request evidence.
    response = client.responses.create(
        model=MODEL,
        input=_build_first_input(system_prompt, candidate, repo_record),
        tools=TOOLS,
        reasoning={"effort": "medium"},
    )

    # Evidence turns, bounded. Each turn: execute requested fetches, chain back.
    turns = 0
    while _function_calls(response) and turns < MAX_TOOL_TURNS:
        outputs = _run_tool_calls(response, snapshot, checked)
        response = client.responses.create(
            model=MODEL,
            previous_response_id=response.id,
            input=outputs,
            tools=TOOLS,
            reasoning={"effort": "medium"},
        )
        turns += 1

    # Turn cap reached with calls still pending: answer each so parse does not
    # chain onto a response with unfulfilled tool calls. Never leave one hanging.
    pending = _function_calls(response)
    if pending:
        budget_outputs = [
            {
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": (
                    "[EVIDENCE BUDGET EXHAUSTED: no further files will be fetched "
                    "this run. Judge with what you have.]"
                ),
            }
            for call in pending
        ]
        response = client.responses.create(
            model=MODEL,
            previous_response_id=response.id,
            input=budget_outputs,
            tools=TOOLS,
            reasoning={"effort": "medium"},
        )

    # Final: parse into the schema, chained onto the evidence conversation.
    parsed = client.responses.parse(
        model=MODEL,
        previous_response_id=response.id,
        input="Now produce the finding for this candidate in the required schema.",
        text_format=Finding,
        tools=TOOLS,
    )
    finding = getattr(parsed, "output_parsed", None)
    if finding is None:
        return None, "model returned no parsed finding"

    err = _validate_finding(finding, valid_names, bare_index)
    if err is None:
        finding.what_checked = _format_what_checked(checked, finding.repo)
        return finding, None

    # One retry with a note, per the floor.
    retry = client.responses.parse(
        model=MODEL,
        previous_response_id=parsed.id,
        input=(
            f"The previous finding failed validation: {err}. "
            "Correct it. The repo must exactly match a repository you were given, "
            "and what_cant_know must name a specific thing GitHub data cannot establish."
        ),
        text_format=Finding,
        tools=TOOLS,
    )
    finding = getattr(retry, "output_parsed", None)
    if finding is None:
        return None, "model returned no parsed finding on retry"
    err = _validate_finding(finding, valid_names, bare_index)
    if err is not None:
        return None, f"validation failed after retry: {err}"
    finding.what_checked = _format_what_checked(checked, finding.repo)
    return finding, None


def reason(candidates, snapshot):
    """
    Run the loop for each candidate. Returns (findings, dropped) where dropped
    is a list of (candidate_full_name, reason) for candidates that failed.
    Model failure retries once inside reason_one; a hard failure drops + logs.
    """
    client = _make_client()
    system_prompt = _load_system_prompt()
    valid_names = _valid_repo_names(snapshot)
    bare_index = _bare_name_index(snapshot)
    by_full = {r.get("full_name"): r for r in snapshot.get("repos", [])}

    findings, dropped = [], []
    for candidate in candidates:
        repo_record = by_full.get(candidate.get("full_name"), {})
        try:
            finding, err = reason_one(
                client, candidate, repo_record, snapshot, system_prompt, valid_names, bare_index
            )
        except Exception as e:
            # Model/network failure: retry once, then drop and log.
            try:
                finding, err = reason_one(
                    client, candidate, repo_record, snapshot, system_prompt, valid_names, bare_index
                )
            except Exception as e2:
                finding, err = None, f"{type(e2).__name__}: {e2}"

        if finding is not None:
            findings.append(finding)
        else:
            name = candidate.get("full_name")
            dropped.append((name, err))
            print(f"DROPPED {name}: {err}", file=sys.stderr)

    return findings, dropped


def main():
    """PASS check: run the loop over a couple of real candidates and show the result."""
    from estate import load_snapshot
    from triage import triage

    if not MODEL:
        print("FAIL: MODEL missing from .env")
        sys.exit(1)

    snapshot = load_snapshot()
    records = triage(snapshot)

    # Pick a small candidate set that has real evidence to read: quiet/long-quiet
    # repos with deployment evidence, so the model has a reason to fetch a file.
    candidates = [
        r
        for r in records
        if r["bucket"] in ("quiet", "long-quiet") and r["has_deployment_evidence"]
    ][:2]
    if not candidates:
        candidates = [r for r in records if r["bucket"] in ("quiet", "long-quiet")][:2]

    print(f"Running the loop over {len(candidates)} candidate(s):")
    for c in candidates:
        print(f"  - {c['full_name']} ({c['bucket']}, deploy={c['has_deployment_evidence']})")
    print("-" * 62)

    findings, dropped = reason(candidates, snapshot)

    for f in findings:
        print(f"\nFINDING: {f.repo}")
        print(f"  why_surfaced: {f.why_surfaced}")
        print(f"  what_checked: {f.what_checked}")
        print(f"  what_found: {f.what_found}")
        print(f"  what_cant_know: {f.what_cant_know}")
        print(f"  recommendation: {f.recommendation} -- {f.recommendation_reason}")
        print(f"  confidence: {f.confidence}")

    print("-" * 62)
    print(f"findings: {len(findings)}, dropped: {len(dropped)}")


if __name__ == "__main__":
    main()
