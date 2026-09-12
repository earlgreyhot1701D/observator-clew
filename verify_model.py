"""
Pre-build verification: proves the model works the way Block 2 needs it to,
before Block 2 exists.

Tests four things independently, so one failure does not hide the others:
  1. Key + model ID resolve (a plain call returns text)
  2. Structured outputs via client.beta.chat.completions.parse (classic path)
  3. Structured outputs via client.responses.parse (newer path)
  4. Function/tool calling (the primitive the agent loop is built on)

Prints a PASS/FAIL table and the installed SDK version. Does NOT decide
anything or write any project logic. Prep-only.

Run: python verify_model.py
"""

import os
import sys
from typing import Literal

try:
    import openai
    from openai import OpenAI
except ImportError:
    print("FAIL: the 'openai' package is not installed. Run: pip install -r requirements.txt")
    sys.exit(1)

try:
    from pydantic import BaseModel
except ImportError:
    print("FAIL: the 'pydantic' package is not installed. Run: pip install -r requirements.txt")
    sys.exit(1)


def load_dotenv(path=".env"):
    """Minimal .env loader, no external dependency."""
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
    results[name] = (ok, detail)
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name}: {detail}")


# A tiny schema shaped like the real one, so this tests what Block 2 will do.
class MiniFinding(BaseModel):
    repo: str
    what_cant_know: str
    recommendation: Literal["SURFACE", "SUPPRESS"]


def main():
    print(f"openai SDK version: {openai.__version__}")
    print(f"MODEL from .env: {MODEL!r}")
    print(f"OPENAI_BASE_URL: {BASE_URL!r}")
    print("-" * 60)

    if not API_KEY:
        print("FAIL: OPENAI_API_KEY is missing from .env. Nothing else can run.")
        sys.exit(1)
    if not MODEL:
        print("FAIL: MODEL is missing from .env. Nothing else can run.")
        sys.exit(1)

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    # 1. Plain call: does the key work and does the model ID resolve?
    try:
        r = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": "Reply with the single word: online"}],
            max_completion_tokens=20,
        )
        text = (r.choices[0].message.content or "").strip()
        record("1. key + model ID", True, f"model responded: {text!r}")
    except Exception as e:
        record("1. key + model ID", False, f"{type(e).__name__}: {e}")
        print("\nStop here. Everything below depends on this. Fix the key or the model ID first.")
        summary()
        return

    # 2. Structured outputs via chat completions. The current docs show
    #    client.chat.completions.parse; older SDKs only have it under .beta.
    #    Try current first, fall back to the legacy alias, report which worked.
    prompt_2 = (
        "Repo 'demo-app' has not been pushed to in 200 days and has a "
        "Dockerfile. Fill the schema. Recommend SURFACE or SUPPRESS."
    )
    for label, accessor in (
        ("2a. structured outputs (chat.completions.parse)", lambda c: c.chat.completions.parse),
        ("2b. structured outputs (beta.chat.completions.parse)", lambda c: c.beta.chat.completions.parse),
    ):
        try:
            fn = accessor(client)
        except AttributeError:
            record(label, False, "method does not exist in this SDK version")
            continue
        try:
            r = fn(
                model=MODEL,
                messages=[{"role": "user", "content": prompt_2}],
                response_format=MiniFinding,
            )
            parsed = r.choices[0].message.parsed
            record(label, parsed is not None, f"parsed -> {parsed!r}")
        except Exception as e:
            record(label, False, f"{type(e).__name__}: {e}")

    # 3. Structured outputs, newer path (responses.parse). May not exist on older SDKs.
    try:
        parse_fn = getattr(getattr(client, "responses", None), "parse", None)
        if parse_fn is None:
            record(
                "3. structured outputs (responses.parse)",
                False,
                "not available in this SDK version (not a problem if #2 passed)",
            )
        else:
            r = parse_fn(
                model=MODEL,
                input=(
                    "Repo 'demo-app' has not been pushed to in 200 days and has a "
                    "Dockerfile. Fill the schema. Recommend SURFACE or SUPPRESS."
                ),
                text_format=MiniFinding,
            )
            parsed = getattr(r, "output_parsed", None)
            record(
                "3. structured outputs (responses.parse)",
                parsed is not None,
                f"parsed -> {parsed!r}",
            )
    except Exception as e:
        record("3. structured outputs (responses.parse)", False, f"{type(e).__name__}: {e}")

    # 4. Tool calling: the agent loop primitive. The model must ASK for evidence.
    tools = [
        {
            "type": "function",
            "function": {
                "name": "fetch_file",
                "description": "Fetch the contents of a file from a GitHub repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repo": {"type": "string"},
                        "path": {"type": "string"},
                    },
                    "required": ["repo", "path"],
                },
            },
        }
    ]
    try:
        r = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "You are assessing repo 'demo-app'. You know only that it is quiet "
                        "and has a Dockerfile. If you need to read a file before judging it, "
                        "call fetch_file."
                    ),
                }
            ],
            tools=tools,
        )
        calls = r.choices[0].message.tool_calls
        if calls:
            record(
                "4. tool calling (agent loop primitive)",
                True,
                f"model requested: {calls[0].function.name}({calls[0].function.arguments})",
            )
        else:
            record(
                "4. tool calling (agent loop primitive)",
                False,
                "API accepted tools but the model did not call one. "
                "Tool calling is wired; the prompt may need to be more directive.",
            )
    except Exception as e:
        record("4. tool calling (agent loop primitive)", False, f"{type(e).__name__}: {e}")

    summary()


def summary():
    print("-" * 60)
    print("SUMMARY")
    for name, (ok, _) in results.items():
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    print()
    print("What to do with this:")
    print("  #1 must pass or nothing runs tomorrow.")
    print("  Any of #2a / #2b / #3 passing means structured outputs work.")
    print("  Use the exact method that passed. Do not switch to another one.")
    print("  #4 passing means the agent can request evidence. That is the agent loop.")


if __name__ == "__main__":
    main()
