# Tasks: Observator Clew

Hand-written before the event. Build window 11:15 AM to 2:30 PM, Sep 12, 2026.

> **Do not use Run all Tasks.** Execute one task at a time, on my instruction, and stop after each. A concurrent run of this list is the exact failure this project's scope gate exists to prevent. Each task has a clock time and a PASS check that a human runs, not you.

Every task names the only files it may touch. Do not touch a file outside that list. Do not start the next task.

---

- [ ] 1. Block 0: Hello (11:15, 10 min)
  - Files: `main.py`, `schema.py`
  - `schema.py`: Pydantic models per `prompts/output_schema.md`
  - `main.py`: send ONE Telegram message, parse_mode HTML, with bold text, italic text, and `ESTATE_OVERVIEW_URL` as a clickable link
  - No triage, no agent, no GitHub calls, no argument parsing
  - PASS: message arrives, bold and italic render, link opens the placeholder page, schema imports
  - _Requirements: 3.2, 5.2, 5.6_

- [ ] 2. Block 1: Triage (11:25, 30 min)
  - Files: `estate.py`, `triage.py`
  - `estate.py`: load `estate-snapshot.json`, nothing else
  - `triage.py`: deterministic buckets, no model calls, one-line reason per repo, print a table
  - PASS: bucket counts sum to total repo count, every repo has a bucket and a reason
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ] 3. Block 2: Agent loop (11:55, 50 min)
  - Files: `investigate.py`, `reason.py`
  - Use the VERIFIED call shape in `design.md` exactly. Ask the director before writing `reason.py`.
  - `reason.py`: model selects candidates and requests evidence, code executes, model judges after seeing real results. `MAX_TOOL_TURNS = 4` enforced in code in this first version.
  - `investigate.py`: execute tool calls, live GitHub fetch reusing the backoff in `snapshot_estate.py`, labeled snapshot fallback on failure
  - Do not pre-fetch everything into one call. Do not try Chat Completions; it cannot work.
  - PASS: model requests at least one `fetch_file`, fetch executes live, the finding references the real content, output validates, every cited fact exists in the snapshot
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 3.1, 3.3, 3.4, 3.5, 3.6, 3.7, 9.3_

- [ ] 4. Block 3: Push and replay (12:45, 30 min)
  - Files: `telegram_out.py`, `bot.py`
  - Briefing per `prompts/telegram_template.md`, funnel header, HTML, length assert, cap at 3 findings, inline buttons with short-id callback_data under 64 bytes
  - `bot.py`: `Application`, job_queue push at startup
  - 4a. Write `runs/latest.json` every run and add `--replay`, the moment the first real run succeeds
  - 4b. Add a bare `/run` handler and confirm a SECOND run fires inside the same running `Application` without a restart
  - 4c. Do one run, decline, re-run cycle and save that second result as a separate rehearsed fallback file
  - PASS: briefing arrives, under 4096, funnel correct, buttons render, `--replay` resends, `/run` triggers a second run in-process
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 6.1, 6.2, 6.3, 9.1, 9.2_

- [ ] 5. Block 4: Decisions (1:15, 35 min)
  - Files: `guard.py`, `bot.py`
  - `guard.py`: policy guard, persistence guard, read/write `state/decisions.json`. The persistence guard runs BEFORE the model is called.
  - `bot.py`: callback handlers. First line of every handler is `await query.answer()`.
  - PASS: tapping No action answers the callback immediately and writes decision plus fingerprint; a second run suppresses that finding, cites the stored decision, and makes no model call for it
  - _Requirements: 4.1, 4.2, 6.4, 6.5, 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 6. Block 5: Estate Overview (1:50, 20 min)
  - Files: `dashboard.py`, `docs/index.html`
  - Render real run data into the existing shell at run end only. Preserve palette tokens, layout, four-part grammar, funnel strip. No JavaScript, no external assets, no CDN.
  - PASS: `docs/index.html` has real data, is pushed, loads at the live Pages URL
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [ ] 7. Block 6: Harden (2:10, 20 min)
  - Files: `README.md` only
  - Fill in "Built during the event" with what was actually built. Be specific and honest. Do not touch "Prepared before the event." Do not describe inherited work as new.
  - The director handles the commit and push.
  - PASS: README accurately separates before and during; no `.env` in the repo
  - _Requirements: 10.1, 10.2, 10.3, 10.4_

---

**FREEZE AT 2:30.** No task after this point. Recording and submission are human work and are not in this list.

**If behind:** stop the current task, report what works, what is half-finished, and what breaks if the half-finished part is deleted. Then wait. The cut order is in `planning/ARCHITECTURE.md` and the director chooses, not you.
