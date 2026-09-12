# Brief to Fable 5.1: final hardening review

You are Fable, an independent evaluator. You have no stake in the decisions already made and no obligation to be encouraging. Your job is to find what will actually go wrong, not to validate what exists.

Read this whole brief before responding. Then read the repository.

---

## Situation

Solo builder. AI Tinkerers "Agents, Everywhere" hackathon, Saturday September 12, 2026, in person, Los Angeles.

- Build window: **11:15 AM to 2:30 PM**, three hours fifteen minutes. Code freeze 2:30.
- Submissions close **3:30 PM**. The hour between freeze and deadline is recording, uploading, the portal form, and the social post.
- It is now late Friday night. The builder needs to sleep. **This is the last review before build day.**

Five required deliverables: project title, written description, public GitHub repo, two-minute demo video, public social post tagging event partners.

Four judging criteria, each scored 1 to 5: Core Requirements & Functionality, Innovation & Theme Alignment, Technical Execution & Integration, Usefulness & Agentic Experience.

Build eligibility rule, verbatim: "You can use existing templates, reusable components, libraries, prompts, starter code, and other building blocks, but the project and its core functionality must be built during the event. A pre-existing project cannot be resubmitted or extended and entered as a new hackathon project. Teams must be prepared to explain which parts were created during the hackathon versus what existed before."

## The project

Observator Clew. An agent that watches one person's GitHub estate (62 repos) and decides what deserves their attention, delivered unprompted to Telegram.

Deterministic triage flags candidates. The agent selects which to investigate, requests specific files as evidence, reads the real results, and recommends SURFACE or SUPPRESS with a reason either way. A deterministic policy guard decides whether that recommendation actually interrupts the human. Inline Telegram buttons record the human's decision with an evidence fingerprint; a persistence guard reads that store **before** the model is called on the next run, so a declined finding with unchanged evidence is skipped without a model call.

Thesis: "Creating is becoming nearly free. Maintaining never did."
Judges' line: "Most agents are designed to say more. Observator is designed to learn when not to bother you."

## Read these, in this order

1. `AGENTS.md`
2. `planning/ARCHITECTURE.md` (the operating document: loop, scope gate, file map, block order with PASS checks, cut order, protect list, demo sequence)
3. `planning/WIND-DOWN.md` (rigor tier, the floor, backstop, wind down)
4. `README.md`
5. `prompts/system_prompt.md`, `prompts/output_schema.md`, `prompts/telegram_template.md`
6. `docs/index.html`
7. The build day runbook, provided separately, not in the repo

---

## Already verified against the real key and model. Do not re-litigate.

These were tested Friday night with live API calls. Treat them as established facts:

- `gpt-6-astra` **cannot** use function tools in `/v1/chat/completions`. Tested. The error suggests `reasoning_effort="none"` as a fallback; that value is **not supported by this model** (only low, medium, high, xhigh). There is no Chat Completions path. Closed door.
- Tool calling works on `/v1/responses`. Verified.
- The full round trip works: model requests a file, code returns content, model reads it and references it. Verified.
- `client.responses.parse` with `text_format=` chained via `previous_response_id`, with tools passed, returns a validated Pydantic object. Verified. Block 2 is one chained loop.
- Latency: 1.2s at low effort, 1.4s at medium, one turn each, single samples.
- Installed and working: `openai 3.13.0`, `python-telegram-bot 22.8`, `pydantic 2.13.5`, `requests 2.34.2`.
- `.env` contains real values for all six keys. Never committed. Confirmed.
- GitHub Pages is live at https://earlgreyhot1701d.github.io/observator-clew/ serving the placeholder shell.

## Locked. Do not reopen unless you can show it is actually broken.

Branding, the thesis and judges' line, the four-part explainability grammar (WHY THIS SURFACED / WHAT I CHECKED / WHAT I FOUND / WHAT I CAN'T KNOW), the funnel header, Python, Telegram as the surface, the demo ending on second-run suppression, and the decision to use no agent framework.

---

## What I want from you

Work through these in order. Be specific. Cite file and line where you can.

**1. The single point of failure.** Walk the demo sequence beat by beat as a hostile reader. Where is the one thing that, if it fails, leaves no demo at all? Is it mitigated? The mitigations claimed are `--replay`, the committed placeholder page, and snapshot fallback. Test those claims against the actual cut order.

**2. The agent question.** A judge asks: "is this really an agent, or is it triage plus a summary?" Read the architecture and answer honestly on the project's behalf. If the honest answer is weak, say so and say exactly which line of code or which demo beat would have to change to make it strong. Do not accept the project's own framing.

**3. Rubric coverage, adversarially.** For each of the four criteria, what would a skeptical judge score this, and what is the single cheapest change that moves the lowest one? "Cheapest" means minutes, and the budget is already at roughly 3h15 against a 3h15 window, so anything you propose must name what it displaces.

**4. Overclaiming.** Read `README.md` and the demo script for anything that is not true, not yet true, or true only under conditions not stated. The project's own stated value is honesty about what it cannot know. An overclaim in the README is worse here than in a normal project. Check the prepared-before / built-during split especially: is the disclosure actually accurate and complete, or does it flatter?

**5. The time budget.** The block plan is Block 0 hello (10 min), Block 1 triage (30), Block 2 agent loop (50), Block 3 push and replay (30), Block 4 decisions (35), Block 5 Estate Overview (20), Block 6 harden (20). Solo, one person, on a clock, with a working verified API. Which estimate is a lie? Name one. There is always one.

**6. What did the previous reviewer miss?** The prior work on this plan made several errors that were caught late: a missing bound on the agent tool loop, a missing prompt rule about retrieved content being data rather than instructions, the Estate Overview URL not recorded in any file so the demo's link beat would have been dead, the Estate Overview having no dedicated demo beat, and no Telegram Desktop setup instructions for someone who has only used the phone app. Assume more of that class exists. Look for things that are *absent* rather than wrong. Absence is what the previous passes kept missing.

**7. The wifi question.** Venue wifi, in person, live demo. Walk the failure modes: wifi drops mid-run, GitHub rate limits, the model is slow, Telegram is unreachable, GitHub Pages has not propagated. Which of these is unhandled?

**8. One sentence: what is the dumbest way this fails?**

---

## How to report. Read this carefully; it changes what you should write.

It is late Friday night. An unbounded list of defensible concerns delivered now is not help, it is harm: it produces a tired builder who cannot sleep and who arrives tomorrow second-guessing a plan that is already reviewed three times. Your value is in triage, not volume.

So:

**Cap your findings at eight.** If you have more, you have not prioritized. Rank by expected cost of not fixing.

**Classify every finding as exactly one of:**

- **TONIGHT**: under fifteen minutes, and not fixing it risks the whole demo. Be extremely reluctant to use this label. Sleep has compounding value and most things are not this.
- **BUILD WINDOW**: fold into a block tomorrow. Say which block and what it displaces, since the budget has no slack.
- **ACCEPT**: real, but the right call is to know it and proceed. Say it plainly so it is a decision rather than a surprise.

**Then, separately, state the three things that are strongest.** Not as encouragement. Because the cut order tomorrow depends on knowing what to protect, and a review that only lists problems produces a builder who cuts the wrong thing at 1:40 PM.

**Do not propose new features.** Not an improvement, not a small addition, not an obvious next step. If a fix requires new scope, say what it displaces from the ten-item scope gate in `planning/ARCHITECTURE.md`. A suggestion that adds work without naming a cut is not a suggestion, it is a wish.

**End with one line:** ship it as planned, ship it with the TONIGHT items, or do not ship this plan. Pick one. Do not hedge.

---

## House rules

No em dashes. No AI clichés (delve, landscape, straightforward, genuinely, honestly, soapbox phrasing). Opinions stated directly, not as declarations of fact. Short and conversational. No flattery. If something is wrong, say it is wrong. If the plan is solid, say that too, and say which part is thinnest.

Verify claims against the actual files. Do not trust this brief's summary of the repository over the repository itself. If this brief contradicts what you find in the files, the files win, and say so.
