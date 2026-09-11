# Observator Clew — Output Schema Spec (v1, prepared before event)

This is a field-by-field spec for Saturday's Pydantic model. Writing the
actual `class Finding(BaseModel): ...` is core functionality and happens
during the event — this file exists so the schema doesn't have to be
designed live, only typed in.

## `Finding` (one per candidate the agent reasoned about)

| Field | Type | Required | Notes |
|---|---|---|---|
| `repo` | str | yes | must match a `full_name` from the snapshot; validate in code |
| `why_surfaced` | str | yes | one sentence, non-empty |
| `what_checked` | list[str] | yes | may be empty list; empty means "no additional evidence requested" |
| `what_found` | str | yes | one to two sentences |
| `what_cant_know` | str | yes | non-empty; reject/retry if the model returns something like "N/A" |
| `recommendation` | Literal["SURFACE", "SUPPRESS"] | yes | enum, not free text |
| `recommendation_reason` | str | yes | non-empty for both SURFACE and SUPPRESS |
| `confidence` | Literal["high", "medium", "low"] | yes | the model's own confidence in the recommendation, not in the facts (facts aren't the model's to be confident about) |

## `RunResult` (the whole run, saved to `runs/latest.json`)

| Field | Type | Notes |
|---|---|---|
| `run_at` | ISO 8601 str | when this run happened |
| `observed_count` | int | total repos in the snapshot |
| `signaled_count` | int | repos the deterministic layer flagged as candidates |
| `investigated_count` | int | candidates actually sent to the model (signaled minus any auto-suppressed by the persistence guard before the model ever ran) |
| `surfaced` | list[Finding] | recommendation == SURFACE and passed the policy guard |
| `suppressed` | list[Finding] | recommendation == SUPPRESS, OR auto-suppressed by the persistence guard (see below) |
| `auto_suppressed_note` | list[str] | one line per repo the persistence guard skipped before the model ran, e.g. "old-hackathon-app: No action, Sep 12 — evidence unchanged" |

`surfaced_count` for the funnel header is `len(surfaced)`, computed, not stored twice.

## Validation rules (code, not prompt)

- Every `repo` value must exist in the snapshot's repo list — reject the
  response and retry once if not (a hallucinated repo name is a hard fail,
  not a warning).
- `what_cant_know` must be non-empty; if the model returns an empty string
  or a placeholder like "none" or "N/A", treat as a schema violation and
  retry once with a note in the retry prompt.
- If retry also fails validation, drop that finding from the run and log it
  — do not crash the whole run over one bad finding, and do not silently
  invent a fallback value for it.

## Decision store (separate file, `state/decisions.json`)

Not part of `Finding` — this is what `[Investigate]` / `[No action]` button
presses write, and what the persistence guard reads before candidates are
even sent to the model.

| Field | Type | Notes |
|---|---|---|
| `repo` | str | key |
| `decision` | Literal["investigate", "no_action"] | what the human chose |
| `decided_at` | ISO 8601 str | |
| `evidence_fingerprint` | object | `{pushed_at, archived, open_issues_count, deploy_files: [sorted list]}` — recomputed each run; if it matches what's stored, the guard suppresses without calling the model |

This file is read/write, not agent output — Saturday's code owns it, not
the prompt.
