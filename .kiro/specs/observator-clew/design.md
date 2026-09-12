# Design: Observator Clew

Hand-written before the event. The full reasoning lives in `planning/ARCHITECTURE.md`; this is the implementation map Kiro works from.

---

## Architecture

```
code                          model
----                          -----
snapshot -> triage
  deterministic, no model
  produces N candidates
                    |
persistence guard   |
  reads state/decisions.json
  drops candidates already declined
  whose fingerprint is unchanged
  (no model call for these)
                    v
                         ->   SELECT: which candidates matter,
                              what evidence do I need?
                              (emits function_call: fetch_file)
fetch_file executed
  live GitHub API
  returns real file contents
                         ->   INTERPRET: what does this evidence mean?
                              RECOMMEND: SURFACE or SUPPRESS + reason
policy guard
  deterministic
  decides whether to interrupt
  -> Telegram briefing + buttons
  -> docs/index.html at run end
```

The round trip is the design. The model requests evidence, code executes, the model sees the real result, then it judges. Collapsing this into one pre-fetched call turns the project into a summarizer.

## Model authority

| Decision | Owner |
|---|---|
| Which repos are candidates | Code, deterministic triage |
| Which candidates to investigate, what evidence to request | Model |
| What the evidence means | Model |
| SURFACE or SUPPRESS, and why | Model |
| Whether a recommendation interrupts a human | Code, policy guard |
| Whether a prior human decision suppresses entirely | Code, persistence guard, runs before the model |
| Any fact: dates, counts, file presence, archive status | Code |

## VERIFIED API shape, tested Friday against the real key

`gpt-6-astra` cannot use function tools in `/v1/chat/completions`. Tested. The error suggests `reasoning_effort="none"`; that value is not supported by this model. There is no Chat Completions path. Do not attempt it.

```python
from openai import OpenAI

# timeout is not optional: half-dead wifi hangs rather than erroring.
client = OpenAI(api_key=OPENAI_API_KEY, timeout=20)

# Responses API uses the FLATTENED tools shape. No nested "function" key.
TOOLS = [{
    "type": "function",
    "name": "fetch_file",
    "description": "Fetch the contents of a file from a GitHub repository.",
    "parameters": {
        "type": "object",
        "properties": {"repo": {"type": "string"}, "path": {"type": "string"}},
        "required": ["repo", "path"],
        "additionalProperties": False,
    },
    "strict": True,
}]

r1 = client.responses.create(
    model=MODEL, input=prompt, tools=TOOLS, reasoning={"effort": "medium"}
)
calls = [i for i in (r1.output or []) if getattr(i, "type", None) == "function_call"]

r2 = client.responses.create(
    model=MODEL,
    previous_response_id=r1.id,
    input=[{"type": "function_call_output",
            "call_id": calls[0].call_id,
            "output": file_text}],
    tools=TOOLS,
)

final = client.responses.parse(
    model=MODEL,
    previous_response_id=r2.id,
    input="Now produce the finding in the required schema.",
    text_format=Finding,
    tools=TOOLS,
)
finding = final.output_parsed
```

`previous_response_id` is within-run conversation state. It is not the memory layer. Memory across runs is `state/decisions.json`.

Measured latency: 1.2s at low effort, 1.4s at medium, single samples. Use medium.

## Files, one responsibility each

| File | Responsibility |
|---|---|
| `main.py` | Entrypoint, wiring, `--replay` |
| `schema.py` | Pydantic `Finding` and `RunResult` |
| `estate.py` | Load `estate-snapshot.json` |
| `triage.py` | Deterministic buckets |
| `investigate.py` | Execute tool calls, live GitHub fetch, labeled snapshot fallback |
| `reason.py` | The agent loop, bounded at MAX_TOOL_TURNS = 4 |
| `guard.py` | Policy guard, persistence guard, `state/decisions.json` |
| `telegram_out.py` | Message build and send, HTML, length assert, inline buttons |
| `bot.py` | `Application`, job_queue push, callback handlers, `/run` |
| `dashboard.py` | Render `docs/index.html` at run end |

No god files. No abstraction for a second use case that does not exist.

## Data shapes

**Finding:** repo, why_surfaced, what_checked (list), what_found, what_cant_know, recommendation (SURFACE or SUPPRESS), recommendation_reason, confidence.

**RunResult:** run_at, observed_count, signaled_count, investigated_count, surfaced (list), suppressed (list), auto_suppressed_note (list of strings).

**Decision record** in `state/decisions.json`: repo, decision (investigate or no_action), decided_at, evidence_fingerprint of pushed_at, archived, open_issues_count, and the sorted deploy-file set.

`surfaced_count` is computed as `len(surfaced)`, never stored twice.

## Error handling

| Failure | Behavior |
|---|---|
| GitHub fetch fails | Fall back to snapshot, label the fallback in output |
| Model output fails validation | Retry once, then drop that finding and log it |
| Model call times out | Fails fast at 20s, recoverable with `--replay` |
| Telegram message too long | Asserted before send, capped at 3 findings |
| callback_data too long | Asserted before keyboard build, short ids only |

## Constraints

One long-running `Application`. Inline button callbacks only resolve while a process is listening, so the second run must fire from inside the same process via `/run` or a second job_queue entry, never by restarting the bot. Decisions survive a restart because they are a file; buttons do not.
