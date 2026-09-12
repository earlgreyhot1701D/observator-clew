"""
Follow-up verification, one question only.

verify_model.py test 4 failed with:
  "Function tools with reasoning_effort are not supported for gpt-6-astra in
   /v1/chat/completions. To use function tools, use /v1/responses or set
   reasoning_effort to 'none'."

The agent loop needs BOTH function tools and reasoning. So this tests whether
tool calling works on /v1/responses, which is what the error points to.

Note the tools shape differs between the two APIs. Chat Completions nests the
function metadata under a "function" key; the Responses API flattens it. This
script uses the flattened shape.

Three tests:
  A. Tool calling on /v1/responses (flattened tools shape)
  B. The full round trip: model requests a tool, we return a result, model
     sees it and answers. This is the actual agent loop, not just tool support.
  C. Chat Completions with reasoning_effort="none", to know what the fallback
     costs if A and B fail.

Run: python verify_tools_responses.py
"""

import json
import os
import sys

try:
    import openai
    from openai import OpenAI
except ImportError:
    print("FAIL: 'openai' not installed. Run: pip install -r requirements.txt")
    sys.exit(1)


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

API_KEY = os.environ.get("OPENAI_API_KEY")
BASE_URL = os.environ.get("OPENAI_BASE_URL") or None
MODEL = os.environ.get("MODEL")

results = {}


def record(name, ok, detail):
    results[name] = ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")


# Flattened shape, required by the Responses API.
RESPONSES_TOOLS = [
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

ASK = (
    "You are assessing the repository 'demo-app'. You know only that it has not "
    "been pushed to in 200 days and that a Dockerfile is present. Before judging "
    "it, read its README by calling fetch_file."
)


def find_function_calls(response):
    """Return function_call items from a Responses API result."""
    calls = []
    for item in getattr(response, "output", []) or []:
        if getattr(item, "type", None) == "function_call":
            calls.append(item)
    return calls


def main():
    print(f"openai SDK version: {openai.__version__}")
    print(f"MODEL: {MODEL!r}")
    print("-" * 62)

    if not API_KEY or not MODEL:
        print("FAIL: OPENAI_API_KEY or MODEL missing from .env.")
        sys.exit(1)

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    # ---- A. Does the model request a tool on /v1/responses? ----
    first = None
    call = None
    try:
        first = client.responses.create(
            model=MODEL,
            input=ASK,
            tools=RESPONSES_TOOLS,
        )
        calls = find_function_calls(first)
        if calls:
            call = calls[0]
            record(
                "A. tool calling on /v1/responses",
                True,
                f"model requested {call.name}({call.arguments})",
            )
        else:
            types = [getattr(i, "type", "?") for i in (getattr(first, "output", []) or [])]
            record(
                "A. tool calling on /v1/responses",
                False,
                f"API accepted tools but no function_call in output. Item types: {types}",
            )
    except Exception as e:
        record("A. tool calling on /v1/responses", False, f"{type(e).__name__}: {e}")

    # ---- B. The full round trip. This is the agent loop. ----
    if call is not None:
        try:
            fake_readme = (
                "# demo-app\n\nInternal tool for generating weekly reports. "
                "Deployed to Cloud Run in March. Superseded by report-service."
            )
            followup = client.responses.create(
                model=MODEL,
                previous_response_id=first.id,
                input=[
                    {
                        "type": "function_call_output",
                        "call_id": call.call_id,
                        "output": fake_readme,
                    }
                ],
                tools=RESPONSES_TOOLS,
            )
            text = (getattr(followup, "output_text", "") or "").strip()
            saw_evidence = "supersed" in text.lower() or "report-service" in text.lower()
            record(
                "B. full round trip (model sees tool result)",
                bool(text),
                f"referenced the returned content: {saw_evidence}. Reply: {text[:220]!r}",
            )
        except Exception as e:
            record("B. full round trip (model sees tool result)", False, f"{type(e).__name__}: {e}")
    else:
        record("B. full round trip (model sees tool result)", False, "skipped, A did not produce a tool call")

    # ---- C. Fallback: chat completions with reasoning disabled ----
    try:
        r = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": ASK}],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "fetch_file",
                        "description": "Fetch the contents of a file from a GitHub repository.",
                        "parameters": RESPONSES_TOOLS[0]["parameters"],
                    },
                }
            ],
            reasoning_effort="none",
        )
        tc = r.choices[0].message.tool_calls
        record(
            "C. fallback: chat completions, reasoning_effort='none'",
            bool(tc),
            f"requested {tc[0].function.name}({tc[0].function.arguments})" if tc else "no tool call made",
        )
    except Exception as e:
        record("C. fallback: chat completions, reasoning_effort='none'", False, f"{type(e).__name__}: {e}")

    print("-" * 62)
    print("SUMMARY")
    for name, ok in results.items():
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    print()
    print("Decision this drives:")
    print("  A and B pass  -> build the agent loop on /v1/responses. Preferred.")
    print("  A or B fails, C passes -> chat completions with reasoning_effort='none',")
    print("                            which means no reasoning. Weaker, still works.")
    print("  All fail -> the loop cannot use tools. Fall back to pre-fetching")
    print("              evidence deterministically and say so plainly in the README.")


if __name__ == "__main__":
    main()
