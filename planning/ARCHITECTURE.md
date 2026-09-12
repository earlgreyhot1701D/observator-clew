# Observator Clew: Architecture Card

One page. Keep this open during the build. Full rationale lives in the build-day review; this is the operating document.

---

## The loop: ReAct, bounded at 4 turns

Say this plainly, in the README and on camera. The pattern is ReAct (reason, act, observe), implemented directly rather than through a framework: the model reasons about what it needs, acts by requesting a tool call, observes the real result, and only then judges.

The model does not receive a finished dossier and write prose about it. It runs a loop:

```
code                          model
----                          -----
snapshot -> triage
  (deterministic, no model)
  produces N candidates
                         ->   SELECT: which candidates matter,
                              and what evidence do I need?
                              (returns tool calls: fetch_file)
fetch_file executed
  (live GitHub API)
  returns real file contents
                         ->   INTERPRET: given the evidence I asked
                              for, what is going on here?
                              RECOMMEND: SURFACE or SUPPRESS + reason
policy guard
  (deterministic)
  validates evidence completeness,
  checks prior human decisions,
  enforces the interruption threshold
  -> Telegram
```

Three things make this agentic rather than a single API call:

1. **The model chooses what to investigate.** Triage produces candidates; the model decides which deserve a closer look and which files to read. That choice is not in the code.
2. **There is a round trip.** The model requests evidence, code executes the fetch, the model sees the result and only then judges. Two model turns minimum, with a real tool execution between them. This is the difference between an agent and a prompt.
3. **Human decisions change future behavior.** A button tap in Telegram writes to a decision store that the guard reads on the next run, before the model is called. The loop closes.

**If you run out of time and pre-fetch everything into one call, you have a summarizer.** Protect the round trip. It is the answer to "is this really an agent?"

**The loop must be bounded.** `MAX_TOOL_TURNS = 4`. The model may request evidence at most four times per run, then the loop exits and it judges with what it has. This is a floor item, not a nicety: an unbounded loop is a model that can keep asking for files until the API bill or the venue Wi-Fi stops it. Write the cap in the first version of `reason.py`, not as a hardening pass. See `WIND-DOWN.md` for the rest of the floor.

**Fetched file contents are untrusted input.** README text from real repos reaches the model. Delimit it clearly and label it as data, never as instructions. The model's authority is already bounded to the output schema and the policy guard is deterministic code it cannot reach, so the worst case is one bad recommendation that a human sees and can decline.

### Locked: the whole build runs on `/v1/responses`

Verified Sep 11 against the real key and model. Two errors, read together:

1. Chat Completions rejected function tools: "Function tools with reasoning_effort are not supported for gpt-6-astra in /v1/chat/completions. To use function tools, use /v1/responses or set reasoning_effort to 'none'."
2. Setting `reasoning_effort="none"` was then rejected: "does not support 'none' with this model. Supported values are: 'low', 'medium', 'high', and 'xhigh'."

The API offered two escape routes and then proved one of them does not exist. **Function tools do not work in Chat Completions on this model, and there is no fallback.** Tool calling and a full round trip both passed on `/v1/responses`.

**This is a closed door, not a preference.** If the loop misbehaves mid-build, do not "just try chat completions." It cannot work. That path is already tested and dead.

Consequences:

- Use `client.responses.create` for the evidence turns and `client.responses.parse` with `text_format=` for the structured finding. Do not mix in `chat.completions`, even though all three parse methods passed in isolation. One loop, one API, one conversation-state mechanism, one tools shape.
- Tools use the **flattened** shape on this API: `{"type": "function", "name": ..., "parameters": ...}`, with no nested `"function"` key. The nested form is Chat Completions only.
- Chain turns with `previous_response_id`. This is within-run conversation state and it is how the loop works. It is **not** the memory layer. Memory across runs stays `state/decisions.json`. Do not confuse the two.
- Pin `reasoning` effort explicitly rather than taking a default you have not timed. A live run on venue wifi with a judge watching makes latency a demo risk, not just a cost line.

### Decision record: plain SDK, no agent framework

**Adopted:** the `openai` Python SDK. It provides structured outputs with Pydantic (the API enforces the output shape rather than the code hoping for it) and tool-calling plumbing. Raw HTTP would produce identical model behavior, since the SDK is a client, but hand-rolling schema enforcement at 12:30 PM is not a good trade.

**Rejected:** every agent framework. The OpenAI Agents SDK, and the ones the starter kit itself names as swappable backends (LangGraph, CrewAI, Mastra, Pydantic AI, Google ADK). Reasons, in order of weight:

1. **The loop is nine lines.** Request, execute, append, repeat, bounded at 4. A framework abstracts a loop that is shorter than its own configuration.
2. **The guards must be visible.** The strongest answer to "is this really an agent?" is showing exactly where the model's authority ends and deterministic code begins. A framework puts its own control flow between those two things, and that is the part judges are being asked to evaluate.
3. **Debuggability under a clock.** The last hour is debugging. An unfamiliar abstraction layer at 1:45 PM is an unbounded risk against a 3:15 submission.
4. **Nothing is gained.** Frameworks earn their place with multi-agent orchestration, persistence, retries across long horizons, or observability. This is one agent, one loop, four turns, one run.

**Independent support for the bound:** the starter kit's own reference agent sets `maxSteps: 10` with the comment that the default of 1 means the agent "can call one tool and then stops, before it ever sees the result. Any agent with tools needs room to loop." Same conclusion, different codebase. Ours is 4 because one run investigates at most a handful of candidates.

### Model authority contract

| Decision | Owner |
|---|---|
| Which repos are candidates at all | Code (deterministic triage) |
| Which candidates to investigate, what evidence to request | Model |
| What the evidence means | Model |
| SURFACE or SUPPRESS recommendation + reason | Model |
| Whether a recommendation actually interrupts the human | Code (policy guard) |
| Whether a prior human decision suppresses this entirely | Code (persistence guard, runs before the model) |
| Any fact: dates, counts, file presence, archive status | Code. The model never restates these differently. |

---

## Files, one responsibility each

| File | Responsibility |
|---|---|
| `main.py` | Entrypoint. Wires the run, handles `--replay`. |
| `schema.py` | Pydantic models: `Finding`, `RunResult`. Per `prompts/output_schema.md`. |
| `estate.py` | Loads `estate-snapshot.json`. Nothing else. |
| `triage.py` | Deterministic buckets. Descriptive names only (`long-quiet`, not `archive-candidate`). |
| `investigate.py` | Executes tool calls the model requests. Live GitHub fetch, snapshot fallback (labeled). |
| `reason.py` | The model loop. Select, request evidence, interpret, recommend. |
| `guard.py` | Policy guard + persistence guard. Reads/writes `state/decisions.json`. |
| `telegram_out.py` | Message build + send. HTML parse mode, 4096 cap, inline buttons. |
| `bot.py` | `Application`, job_queue push at startup, callback handlers for the buttons. |
| `dashboard.py` | Renders `docs/index.html` at run end only. Not on button tap. |

Create `state/.gitkeep` so the decision store has a home. `state/decisions.json` is not gitignored; commit it after the demo so persistence is visible to judges.

### The Estate Overview link

`ESTATE_OVERVIEW_URL` in `.env` is the live GitHub Pages URL: `https://earlgreyhot1701d.github.io/observator-clew/`. Every Telegram briefing ends with `<a href="{estate_overview_url}">View full estate</a>`, and tapping it is the receipt beat of the demo at 1:05.

Read it from env, never hardcode it. Put the link in the very first message you send in Block 0, before any real data exists, so a broken URL surfaces at 11:20 rather than on camera. The page it opens will say `[placeholder]` everywhere at that point, and that is the correct result: what Block 0 proves is that the link works, not that the page has content.

Cutting the Estate Overview (cut-order item 3) does not cut the link. It falls back to the committed placeholder shell, which is already deployed and already loads.

---

## Build order

Start 11:15. **Freeze 2:30.** Phone alarm at 2:25.

| Block | Clock | Files | PASS check |
|---|---|---|---|
| 0. Hello | 11:15–11:25 | `main.py`, `schema.py` | "Observator online" arrives in Telegram **with a working Estate Overview link in it**, HTML renders, the link opens the placeholder page. Schema imports. |
| 1. Triage | 11:25–11:55 | `estate.py`, `triage.py` | Bucket counts sum to total repo count. Every repo has a bucket and a one-line deterministic reason. Printed as a table. |
| 2. Agent | 11:55–12:45 | `investigate.py`, `reason.py` | Model requests at least one `fetch_file`. Fetch executes live. Model sees result and returns validated structured output. Every cited fact exists in the snapshot. |
| 3. Push | 12:45–1:15 | `telegram_out.py`, `bot.py` | Real briefing arrives. Under 4096 chars. Funnel header correct. Buttons render. **Write `runs/latest.json` and build `--replay` here, the moment the first run succeeds.** |
| **1:15 checkpoint** | | | **A real briefing with real findings is in Telegram.** |
| 4. Decisions | 1:15–1:50 | `guard.py`, `bot.py` | Tap No action → ack message. Decision + evidence fingerprint written. Re-run → that finding is suppressed with the stored reason, and no model call was made for it. |
| 5. Overview | 1:50–2:10 | `dashboard.py` | `docs/index.html` written with real data, pushed, loads at the Pages URL. |
| **2:15 checkpoint** | | | **All demo beats work.** |
| 6. Harden | 2:10–2:30 | `README.md` | Built-during section filled in. Committed and pushed. |
| Freeze | 2:30 | | Stop building. |
| Record | 2:30–3:00 | | Screen recording first, voiceover second. Two takes max. |
| Submit | 3:00–3:25 | | Upload, portal form, social post. |

---

## Scope gate

**These ten things are the build. Nothing else ships.**

1. Load snapshot, deterministic triage into descriptive buckets
2. Agent selects candidates and requests evidence; live GitHub fetch, snapshot fallback labeled
3. Structured output with the four-part grammar, recommendation and reason, validated in code
4. Policy guard and persistence guard, keyed on evidence fingerprint
5. Unprompted Telegram push via job_queue, HTML, under 4096 chars, funnel header
6. Inline decision buttons, decision persisted to `state/decisions.json`
7. Second-run suppression citing the stored decision
8. Estate Overview rendered at run end to `docs/index.html`
9. `--replay`
10. Public repo, README with the built-during disclosure filled in

**STUB, not build:** `/check`, `/estate`, Trigger.dev, email, CopilotKit, private repos, multi-provider, charts, deployment liveness checks, voice, any second surface. A stub is a comment naming the thing and why it was deferred. It is not a half-feature.

**If you are ahead of schedule, the answer is no.** Ahead means the next block starts early, or you run the two-snapshot diff, which is the single approved STRETCH. It does not mean a new feature. A good idea arriving at 1:40 PM is still a good idea on Sunday, and it costs nothing to write it down instead of building it.

**If a coding agent proposes something not on the list above, decline it.** It will propose one reasonable thing at a time, and each one will be defensible on its own. That is the failure mode, not a sign the idea is good.

The only thing that overrides this list is a PASS check failing. Then you cut, in the order below.

## Cut order and protect list

**Cut in this order when behind:**
1. Estate Overview re-render on button tap (already cut)
2. Live GitHub fetch → snapshot-only, clearly labeled in output
3. Estate Overview entirely, fall back to the committed placeholder shell
4. Plain text instead of HTML if formatting fights back

**Never cut, in any scenario:**
1. Telegram push
2. Decision buttons
3. Persisted decision
4. Second-run suppression
5. `--replay`
6. Evidence receipt (the four-part grammar)

**Never, at any point:** touch the system prompt after Block 2 passes. Show a terminal with secrets on camera. Build past 2:30.

---

## Demo sequence, locked

Desktop screen recording. Telegram Desktop, Estate Overview in a browser tab. Do Not Disturb on. Start recording already inside the bot chat, never swipe to the chat list.

**One process for the whole demo.** Inline button callbacks only resolve while a process is listening on that bot token. If you kill the bot and run `python main.py` again for the second run, the buttons from run one are dead and the tap does nothing on camera. The second run must be triggered from inside the same running `Application`: a `/run` command handler, or a second `job_queue.run_once`. Build it that way in Block 3, not as a fix at 2:20. The decision store is a file, so the *decisions* survive a restart. The *buttons* do not.

| Time | Beat | What you say |
|---|---|---|
| 0:00–0:12 | Problem. GitHub profile, cut to Telegram. | "I have sixty repositories. Creating them was cheap. Knowing which ones still need me is not. Today, one message told me." |
| 0:12–0:45 | The briefing, already waiting. Read one finding. | "I didn't ask. It observed sixty, signaled seven, investigated three, surfaced two." Point at WHAT I CAN'T KNOW. |
| 0:45–1:05 | Tap No action. | "Decision recorded. I won't surface this again unless the evidence materially changes." |
| 1:05–1:25 | Tap Investigate, open Estate Overview. | "Every claim has a receipt. GitHub can show a deployment was configured. It can't prove it's still alive, so Observator says that instead of guessing." |
| 1:25–1:48 | Run again. The suppression line. | "I told it once. It remembered." |
| 1:48–1:58 | Close. | "Creating is becoming nearly free. Maintaining never did. Most agents are designed to say more. Observator is designed to learn when not to bother you." |

Target 1:55. Hard cap 2:00; upload tools round up.

---

## Judging criteria, and where each is earned

| Criterion | Where it's earned |
|---|---|
| Core Requirements & Functionality | One complete workflow, live, end to end. `--replay` is the insurance. |
| Innovation & Theme Alignment | Say out loud that the decisions live in the surface. Remove Telegram and you lose the interrupt, the decision UI, and the memory of what was dismissed. |
| Technical Execution & Integration | The round trip (model requests evidence, code fetches, model judges). Schema validation with retry. The snapshot fallback, labeled. |
| Usefulness & Agentic Experience | The buttons are user control. The suppression is the agent respecting it. The four-part grammar is understandable feedback. |

The rubric asks for a failure or cancellation path. Yours is the No action tap plus the schema validation retry. Name both.

---

## Deliverables (all five required)

1. Project title
2. Written description: what it does, who it's for, why the context matters
3. Public GitHub repo with run instructions
4. Two-minute demo video
5. Public social media post tagging event partners per organizer instructions

---

*AI assisted. Human approved. Powered by NLP.*
