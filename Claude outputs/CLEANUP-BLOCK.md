# Observator Clew: Cleanup and Improvement Block

**Do not build anything in this document during Blocks 3 through 6.** This is a parking lot, and that is its whole function. Every item here was noticed while the build was running, each one is individually defensible, and building them in sequence is exactly how a 3h15 window becomes 4h30. Re-evaluate after Block 6 passes, or after the event.

Captured Sep 12, 2026, during the build.

---

## Disposition key

- **FIX IF TIME**: real, small, worth doing after Block 6 if the clock allows
- **AFTER EVENT**: real, but not worth touching today
- **DECIDED, DO NOT REVISIT**: already settled, recorded so it does not get reopened by a tired brain at 2 PM
- **ACCEPTED**: known, left alone deliberately

---

## FIX IF TIME

**`confidence` is always `medium`, so the field carries no information.** Nothing defines what high, medium, or low mean, so the model parks in the safe middle on every finding. It is also a self-report, which is the same failure class as the old model-reported `what_checked`. Two options, pick one, not both:

1. Give the field to code, the way `what_checked` was handled. Derive it from evidence completeness, which code already knows: all requested fetches live with no fallback is high; live evidence but something notable uninspected, such as `open_issues_count` above zero, is medium; any fallback or zero files fetched is low. This changes what the word means to "how complete was the evidence," which is a fact code owns and can be defended out loud.
2. Drop the field. A field that cannot carry information is better removed than displayed.

Not urgent: `confidence` does not appear in the Telegram briefing, so it is invisible on camera. It is only readable by someone reading the code or the schema. Option 1 needs about ten minutes in `reason.py` and no prompt change. Option 2 needs two.

**Audience-facing uses of the word "estate."** It is internal vocabulary. A judge reading "View full estate" in a Telegram message or "GitHub estate" in the README has to infer it. The funnel line gives enough context that it mostly survives, and the page name Estate Overview is locked branding, so this is a wording pass and not a rename. Audit the reader-facing strings only: the Telegram link text, the quiet-run message, and the README's first two paragraphs. Everything internal can keep the word.

**`import json` is inside `_run_tool_calls` in `reason.py`.** Kiro flagged it deliberately rather than as an oversight. Move it to the top of the file. Thirty seconds, cosmetic, zero risk.

---

## AFTER EVENT

**`reason.py`'s `main()` is a Block 2 PASS harness, not a second surface.** It should go away once `main.py` wires the real run. Leaving it is harmless today and it is a useful way to exercise the loop in isolation, but it is duplicate entry-point logic and should not survive into anything that outlives the hackathon.

**The GitHub fallback returns presence, not contents.** `_snapshot_fallback` can only report that a file existed in the snapshot, because the snapshot never stored file bodies. It is correctly labeled, so nothing is dishonest, but if GitHub is unreachable the agent is judging from metadata alone and finding quality collapses. Any real version of this would cache file contents for candidates at snapshot time.

**`MAX_CONTENT_CHARS = 4000` truncates mid-file.** If a README puts its deployment URL below the cutoff, the model never sees it and the URL rule in the prompt cannot fire. Today's READMEs are short enough that it has not bitten. A real fix is content-aware truncation, which is over-engineering for a hackathon.

**Open issues are named but never inspected.** The model correctly says so in `what_cant_know`, which is the honest outcome, but `fetch_file` reaches the Contents API only and cannot read issues. Adding an issues tool is a new capability, not a cleanup.

**Two-snapshot diff.** The only approved stretch item from the build plan, still unbuilt. Take a second snapshot and diff it against Thursday's to make "what changed since" real rather than inferred. Genuinely nice, genuinely not required.

---

## DECIDED, DO NOT REVISIT

**No deployment liveness checking.** No HEAD, no GET, no fetch of any deployed URL, no new tool. An HTTP 200 does not prove an application works: a static shell returns 200 with a dead API key behind it, parked domains answer, broken deployments still serve pages. A 404 does not prove abandonment. A liveness check would manufacture confidence the evidence cannot support, which contradicts the project's central claim. Naming the target and stating that liveness is unverifiable is the honest maximum. This was considered twice and declined twice.

**No Chat Completions, ever.** `gpt-6-astra` cannot use function tools there, and the fallback the error suggests, `reasoning_effort="none"`, is not a supported value for this model. Tested twice. If the loop misbehaves, the answer is somewhere else.

**`prompts/system_prompt.md` is frozen.** Frozen when Block 2 passed. Any prompt idea from here on belongs in this document, not in the prompt. Prompt tuning under a clock is where solo builders lose forty minutes and end up worse.

**No agent framework.** The loop is short enough that a framework would abstract something smaller than its own configuration, and the guards need to stay visible because they are the part being evaluated.

---

## ACCEPTED

**`insufficient-evidence` bucket is 0.** Every repo in the snapshot has a `pushed_at`, so the branch never fires. It exists for correctness and costs nothing. Kiro flagged it rather than removing it, which was the right call.

**GitHub token expiration is unchecked.** If it expires mid-run, `investigate.py` falls back to the snapshot and labels it. Costs the live-fetch polish, not the demo.

**The cross-repo guard in `what_checked` may never trigger.** `fetch_file` takes a repo parameter so a cross-repo fetch is possible, and the formatter handles it. It should stay even if it never fires, because a code-owned field should not be capable of hiding anything.

---

## Verify before submitting, not a cleanup item

The bucket definition changed mid-build: deployment evidence moved from being a bucket to an orthogonal boolean, and `requirements.md` plus `ARCHITECTURE.md` were corrected to match. Before submitting, confirm the spec and the code still agree, because a judge reading both side by side is exactly the reader those documents exist for.

---

*AI assisted. Human approved. Powered by NLP.*
