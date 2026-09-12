"""
Last verification. One question: what shape is the loop?

Known so far:
  - Function tools do NOT work in /v1/chat/completions on gpt-6-astra. The
    suggested fallback (reasoning_effort="none") is not a supported value for
    this model. There is no fallback. /v1/responses is the only path.
  - Tool calling and the full round trip both work on /v1/responses.
  - responses.parse works for structured output.

Unknown: can the FINAL structured answer come out of the same chained
conversation that gathered the evidence? That decides whether Block 2 is one
loop or two phases.

  D. responses.parse with tools + previous_response_id (one clean loop)
  E. two-phase fallback: create() gathers evidence, a separate parse() call
     chained to it produces the schema
  F. latency at low / medium reasoning effort, because a live run on venue
     wifi with a judge watching is a demo risk, not just a cost question

Run: python verify_loop_shape.py
"""

import os
import sys
import time

try:
    import openai
    from openai import OpenAI
except ImportError:
    print("FAIL: 'openai' not installed.")
    sys.exit(1)

from pydantic import BaseModel
from typing import Literal


def load_dotenv(path=".env"):
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
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url=os.environ.get("OPENAI_BASE_URL") or None,
)
MODEL = os.environ.get("MODEL")

results = {}


def record(name, ok, detail):
    results[name] = ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")


class MiniFinding(BaseModel):
    repo: str
    what_found: str
    what_cant_know: str
    recommendation: Literal["SURFACE", "SUPPRESS"]


TOOLS = [
    {
        "type": "function",
        "name": "fetch_file",
        "description": "Fetch the contents of a file from a GitHub repository.",
        "parameters": {
            "type": "object",
            "properties": {
                "repo": {"type": "string"},
                "path": {"type": "string"},
            },
            "required": ["repo", "path"],
            "additionalProperties": False,
        },
        "strict": True,
    }
]

ASK = (
    "Assess repository 'demo-app'. You know only that it has not been pushed to "
    "in 200 days and a Dockerfile is present. Read its README with fetch_file "
    "before judging it."
)
FAKE_README = (
    "# demo-app\n\nInternal tool for generating weekly reports. Deployed to "
    "Cloud Run in March. Superseded by report-service."
)


def gather_evidence():
    """Turn 1 and 2: model asks for a file, we hand it back. Returns last response id."""
    first = client.responses.create(model=MODEL, input=ASK, tools=TOOLS)
    calls = [i for i in (first.output or []) if getattr(i, "type", None) == "function_call"]
    if not calls:
        return None, "model made no tool call"
    call = calls[0]
    second = client.responses.create(
        model=MODEL,
        previous_response_id=first.id,
        input=[{"type": "function_call_output", "call_id": call.call_id, "output": FAKE_README}],
        tools=TOOLS,
    )
    return second.id, None


def main():
    print(f"openai {openai.__version__}  model {MODEL!r}")
    print("-" * 62)

    if not MODEL:
        print("FAIL: MODEL missing from .env")
        sys.exit(1)

    # ---- D. one loop: parse() chained onto the evidence conversation ----
    try:
        last_id, err = gather_evidence()
        if err:
            record("D. single-loop (parse chained to evidence)", False, err)
        else:
            r = client.responses.parse(
                model=MODEL,
                previous_response_id=last_id,
                input="Now produce the finding for demo-app in the required schema.",
                text_format=MiniFinding,
                tools=TOOLS,
            )
            parsed = getattr(r, "output_parsed", None)
            record(
                "D. single-loop (parse chained to evidence)",
                parsed is not None,
                f"{parsed!r}",
            )
    except Exception as e:
        record("D. single-loop (parse chained to evidence)", False, f"{type(e).__name__}: {e}")

    # ---- E. two-phase fallback: same, but no tools on the parse call ----
    if not results.get("D. single-loop (parse chained to evidence)"):
        try:
            last_id, err = gather_evidence()
            if err:
                record("E. two-phase (parse without tools)", False, err)
            else:
                r = client.responses.parse(
                    model=MODEL,
                    previous_response_id=last_id,
                    input="Now produce the finding for demo-app in the required schema.",
                    text_format=MiniFinding,
                )
                parsed = getattr(r, "output_parsed", None)
                record("E. two-phase (parse without tools)", parsed is not None, f"{parsed!r}")
        except Exception as e:
            record("E. two-phase (parse without tools)", False, f"{type(e).__name__}: {e}")
    else:
        record("E. two-phase (parse without tools)", True, "skipped, D passed so this is unnecessary")

    # ---- F. latency, because a slow live run on camera is a demo risk ----
    for effort in ("low", "medium"):
        try:
            t0 = time.time()
            client.responses.create(
                model=MODEL,
                input=ASK,
                tools=TOOLS,
                reasoning={"effort": effort},
            )
            record(f"F. latency at reasoning effort '{effort}'", True, f"{time.time() - t0:.1f}s for one turn")
        except Exception as e:
            record(f"F. latency at reasoning effort '{effort}'", False, f"{type(e).__name__}: {e}")

    print("-" * 62)
    print("SUMMARY")
    for name, ok in results.items():
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    print()
    print("Decision this drives:")
    print("  D passes -> Block 2 is one chained loop. Simplest. Build this.")
    print("  D fails, E passes -> gather with create(), then one final parse()")
    print("                      call for the schema. One extra call per run.")
    print("  Both fail -> gather evidence, then start a fresh parse() call with")
    print("               the evidence pasted into the input. Always works.")
    print("  F tells you which reasoning effort to pin so a live run does not")
    print("  stall on camera. Multiply by candidates investigated per run.")


if __name__ == "__main__":
    main()
