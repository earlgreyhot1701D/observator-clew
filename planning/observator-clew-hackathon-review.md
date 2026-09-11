# Observator Clew: Hackathon Scoping Review

**Purpose:** Synthesize and pressure-test the ChatGPT analysis of scoping Observator Clew for the AI Tinkerers hackathon (Saturday, September 12, 2026). Strengths, weaknesses, and every assumption checked against source material.

**Source documents reviewed:**
- Observator Clew PRD (860 lines, concept/pre-validation)
- AI Tinkerers hackathon recap (handbook-derived)
- ChatGPT analysis (two rounds: initial scoping + agent architecture clarification)
- Claude analysis (prior session: sponsor research, feasibility assessment)

---

## What both analyses agree on

The core thesis is strong. "Creating is becoming nearly free. Maintaining never did." That line works in a hackathon room full of builders who all have repo graveyards. You ARE the target user described in the PRD (Section 4: "developer or vibecoder with dozens of repositories"). 60+ repos. The demo is personal, not hypothetical.

Telegram fits the hackathon theme. The theme says "build an agent for a place people already work, talk, or live." Telegram is where you already get messages. The agent shows up there.

The hackathon build is a believable first slice of the full PRD, not a throwaway gimmick. That matters for the pitch and for what happens after Saturday.

---

## Strengths of the ChatGPT analysis

### 1. The "agent vs. cron job" distinction is the right question to ask

ChatGPT caught the most important design problem: a scheduled GitHub digest is automation, not an agent. The fix is correct. The cron is the alarm clock. Observator is the agent that wakes up, decides where to look, gathers evidence, and decides whether to interrupt you. That distinction is what makes this entry fit the hackathon theme instead of being "GitHub Wrapped, but every morning."

The agentic loop ChatGPT describes (observe → rank → decide to investigate → gather more evidence → evaluate → decide whether to notify) is architecturally sound and directly supported by the PRD's own architecture (Section 23: Provider Adapters → Evidence Collectors → Triage/Ranking → Agent Reasoning → Findings + Decision → Human Decision Layer).

### 2. The model authority contract is well-scoped

ChatGPT gives the agent three jobs: (1) choose which repos deserve deeper investigation, (2) decide what the evidence means, (3) decide whether to interrupt you. Everything factual stays deterministic. This is consistent with the PRD's Product Principle 6.2 ("Deterministic facts before probabilistic interpretation") and with the Porch Light model authority contract pattern.

### 3. "Deployment evidence detected" vs. "this is deployed" is exactly right

The PRD itself says (Section 16): "A repository can suggest infrastructure exists; it cannot reliably prove that infrastructure is live." ChatGPT's phrasing, "Observator cannot verify from GitHub alone whether this deployment remains active," directly mirrors the PRD's mitigation strategy: "label inferred versus verified evidence and use Investigate when external state matters."

This is one of the strongest demo moments. It shows the difference between verified facts, inference, and unknowns. That's more interesting than pretending the model is omniscient.

**Post-rubric update:** The Technical Execution criterion explicitly rewards "thoughtful failure handling." Saying "I don't know" with precision IS thoughtful failure handling. This is a direct scoring advantage most hackathon projects don't have.

### 4. The Telegram message format is good

Leading with "3 things worth knowing" instead of dumping stats. The estate summary line at the bottom. The "View your estate" link. That format respects the user's attention and demonstrates the PRD's Product Principle 6.11 (FR-11: "Prioritize consequential findings instead of an unbounded issue list") and Principle 6.5 ("'Do nothing' is a successful recommendation").

### 5. The NO_NOTIFICATION instruction is the single most important feature

"You are not rewarded for finding something every run. If no evidence changes what the user should know or do, return NO_NOTIFICATION." This directly implements PRD Section 17: "If every scan produces red badges, users will stop opening it. Optimize for decision quality and reduced ownership burden, not engagement."

**Post-rubric update:** This is now the scoring linchpin. The Innovation criterion says a score of 2 is "the environment mostly serves as a wrapper." If Observator always sends a Telegram message, Telegram is a delivery pipe. A wrapper. A 2. The agent's decision about WHETHER to interrupt is what makes Telegram essential to the experience, not decorative. This is the difference between a 2 and a 4-5 on Innovation. Build this first, demo this clearly.

### 6. The demo script is strong

Open Telegram → agent tells you what changed → tap through to dashboard → click one finding → see evidence and unknowns → close with the thesis. Two minutes, clear narrative arc. Beginning, middle, end.

---

## Weaknesses of the ChatGPT analysis

### 1. Underestimates the GitHub API integration time

ChatGPT lists GitHub metadata collection as a simple step. In reality, collecting the signals the PRD requires (Section 8: activity, archived state, languages, README, license, topics, releases, issues, workflows, scheduled workflows, dependency manifests, infrastructure-as-code indicators, deployment configuration, domain/config references, homepage URLs, and external-service references) across 58+ repos means:

- Multiple GitHub API endpoints per repo (repos, contents, workflows, languages, issues)
- Rate limiting (5,000 requests/hour for authenticated users, but 58 repos × ~6 endpoints = 348 calls minimum)
- Pagination for repos with many issues, workflows, or files
- Parsing file contents (README, package.json, Dockerfile, vercel.json, etc.) requires individual API calls

This is not a 30-minute task. In a 4-hour build, this could eat 60-90 minutes if you're wiring it live. Mitigation: pre-snapshot your repos into JSON before Saturday (allowed under rules).

### 2. The dashboard scope is vague

ChatGPT shows an ASCII mockup of the dashboard but doesn't address how it gets built. A "single hosted page" that shows estate overview, needs-attention items, and evidence per finding is still a frontend build. Options:

- Static HTML generated by the agent (cheapest, most buildable)
- A minimal Next.js or React page (adds build/deploy time)
- A hosted artifact page (no deploy infrastructure needed)

Recommendation: Static HTML generated as part of the agent run. The agent writes the dashboard. No frontend framework. No deploy pipeline. Just an HTML file hosted on Cloud Run or a static host.

### 3. Telegram bot setup is not as trivial as implied

ChatGPT says "create the Telegram bot via BotFather, takes 2 minutes." Creating the bot token takes 2 minutes, yes. But wiring up:

- Webhook vs. long polling
- Message formatting (Telegram's MarkdownV2 is famously picky)
- Bot command handlers (/estate, /check, /brief)
- Inline keyboard buttons for navigation
- Error handling when the API is down

That's 45-60 minutes of integration work, not 2 minutes. The token is the easy part.

### 4. Trigger.dev integration is assumed but not verified

ChatGPT says "Trigger.dev is sitting right there as a sponsor" and recommends using it for the scheduled job. This is correct strategically (sponsor alignment), but:

- Trigger.dev is a TypeScript-first platform. If the agent is built in Python (Shara's stronger language for agent work), there's a language mismatch.
- Wiring Trigger.dev means learning their SDK, their project structure, and their deployment model. In 4 hours, that's a non-trivial learning curve if you haven't used it before.
- The alternative: a manual trigger button that simulates the cron. Demo it as "this runs on a schedule; I'm triggering it now for the demo." Judges understand this.

Decision needed: Is the Trigger.dev integration worth the build time for sponsor alignment, or is a manual trigger + a stub comment ("Trigger.dev integration point") sufficient?

### 5. The "three commands" scope needs re-evaluation

~~In 4.25 hours with GitHub API + Telegram bot + agent reasoning + dashboard, building three distinct Telegram command handlers is ambitious. /estate (full summary) is the one that demos. /check and /brief are nice-to-haves that could become stubs.~~

**Post-rubric update:** /check deserves reconsideration. The Usefulness criterion asks whether the agent is "intuitive, effective, and appropriate for the environment." Being able to ASK Observator about a specific repo ("/check porch-light") makes Telegram a conversation, not a one-way notification pipe. That lifts both Innovation (environment shapes the interaction) and Usefulness (context-intelligent, controllable). /estate is MUST. /check is a strong stretch goal that could move the Innovation score. /brief stays a stub.

### 6. CopilotKit gets dismissed too quickly

ChatGPT says "stub it." But CopilotKit is a React framework for building copilots INTO apps. If the dashboard is a React page, CopilotKit could add a "talk to your estate" sidebar with relatively little code. The question is whether the dashboard is React at all (see weakness #2). If it's static HTML, CopilotKit doesn't fit. If it's React, CopilotKit is actually one of the faster sponsor integrations.

---

## Assumptions refuted or corrected

### ASSUMPTION: "58 repositories" is accurate
**STATUS: Close but check.** The recap doc says "60 public GitHub repos." ChatGPT uses 58 throughout its examples. The exact number changes as repos are created. Use the real count on demo day.

### ASSUMPTION: September 12, 2026 is a Friday
**STATUS: Corrected.** September 12, 2026 is Saturday. Both ChatGPT and the original recap had this wrong. Fixed in the recap doc.

### ASSUMPTION: The hackathon has sponsor-specific prizes
**STATUS: Unverified.** The recap says "Using a sponsor's tool or API is a strategic advantage. It signals engagement with the ecosystem and may factor into sponsor-specific prizes." The handbook does not explicitly confirm sponsor-specific prizes. This was an inference. It's a reasonable one (most hackathons with sponsors do offer them), but it's not confirmed.

### ASSUMPTION: Trigger.dev supports the scheduled cron pattern described
**STATUS: Verified direction, not implementation.** Trigger.dev's description from sponsor research: "durable AI agent workflows in TypeScript, human-in-the-loop approval workflows, LLM observability." It does support scheduled tasks and background jobs. But it is TypeScript-native. If the agent is Python, Trigger.dev becomes a wrapper/orchestrator calling a Python process, not the agent runtime itself.

### ASSUMPTION: You can pre-prep mock data before the hackathon
**STATUS: Verified.** The hackathon rules (from the recap): "You can use existing templates, libraries, starter kits, and components, but the core functionality has to be built that day." A JSON snapshot of your GitHub repos is data, not core functionality. The agent logic is the net-new part.

### ASSUMPTION: OpenRouter is useful for "model flexibility"
**STATUS: True but low demo value.** OpenRouter gives you a unified API across LLMs. You could swap models without code changes. But in a 2-minute demo, nobody cares which model runs the reasoning. The reasoning quality matters, not the router. Unless there's a sponsor-specific prize for OpenRouter, it adds integration work for negligible demo value. Use whichever model API is fastest to wire (likely OpenAI, since they're the marquee sponsor, or OpenRouter if a single API key is simpler).

### ASSUMPTION: The "previous snapshot" comparison is simple
**STATUS: Harder than it sounds.** ChatGPT's MUST list includes "Save a previous snapshot" and "Compare current vs previous state." For the hackathon demo, this means:

- Run the agent once to establish baseline
- Run it again to show the comparison

This is actually a good demo technique: run it twice, show that the second run knows what changed. But the snapshot storage needs to be solved (JSON file? Database? In-memory?). Simplest: write a JSON file after each run, read the previous one at the start of the next run.

### ASSUMPTION: The dashboard can be "tiny" and still demo well
**STATUS: Agree, with two caveats.** A single-page HTML dashboard showing estate stats and findings is sufficient for the demo. But it needs to look good enough on camera for the 2-minute video. A raw HTML table won't land the same way as a clean, styled page. Budget 30-45 minutes for the dashboard HTML/CSS, or use a CSS framework that's already familiar.

Second caveat: **the dashboard must be mobile-friendly.** Users tap the Telegram link on their phone. That's the natural flow. If the dashboard requires a desktop browser, the demo story has a gap right where it should be seamless. Use responsive design from the start: single-column layout, no fixed-width tables, readable at 375px. This is not optional polish. It's how the product actually gets used.

### ASSUMPTION: Solo is the right call for this build
**STATUS: Agree.** The "this is MY estate" angle is the entire pitch. A teammate doesn't add to that story. The domain knowledge is yours. The repo graveyard is yours. Solo builds also eliminate coordination overhead in a 4-hour window. Your wins are split across solo and team, but this idea is strongest solo.

### ASSUMPTION: Exa is a stretch
**STATUS: Agree.** Exa does AI-native semantic search over the web. You could theoretically use it to search for "is this dependency deprecated?" or "does this project's homepage still resolve?" But that's adding a third API integration (GitHub + Telegram + Exa) to a build that's already tight. Skip unless you finish early.

### ASSUMPTION: Auth0 is not mentioned
**STATUS: Correct omission.** For a demo with hard-coded credentials, Auth0 adds zero demo value and significant build time. Auth is a V2 concern.

---

## The build-day risk matrix

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| GitHub API rate limiting | Medium | High (blocks all data) | Pre-snapshot repos into JSON before Saturday. Carry the snapshot as mock data. Wire live API as stretch goal. |
| Telegram MarkdownV2 formatting bugs | High | Medium (ugly messages, not broken) | Test message formatting before Saturday with the bot token. Have a plain-text fallback. |
| Agent reasoning produces bad findings | Medium | High (demo looks unreliable) | Constrain the model tightly. Three jobs, structured output, evidence-anchored. Test with your actual repos before Saturday. |
| Dashboard takes too long to build | Medium | Low-Medium (judges score the agent in its environment, which is Telegram, not the dashboard) | The dashboard is the evidence receipt, not the scored surface. If time is tight, cut the dashboard to bare minimum before cutting Telegram interaction depth. Static HTML, no framework, mobile-friendly. |
| Trigger.dev integration eats build time | Medium | Low (manual trigger works) | Stub it. Manual trigger for the demo. Comment: "Trigger.dev scheduled workflow integration point." |
| Scope creep into full PRD features | High | High (nothing finishes) | Print the MUST/STUB/NEVER list. Tape it to the laptop. The last NEVER row: "Build the complete Observator PRD." |

---

## Revised MUST / STUB / NEVER (synthesized from both analyses)

### MUST (build day, 4 hours flat, submissions at 3:30 PM)

1. GitHub repo metadata collection (from pre-snapshot JSON, with live API as stretch)
2. Deterministic triage: bucket repos by activity signals (active / stale / dormant / archive-candidate) using pure code logic
3. Agent reasoning: LLM inspects triaged repos, decides which deserve investigation, gathers evidence (README, config files), produces plain-language findings with evidence citations
4. **Agent decides whether to notify (NO_NOTIFICATION if nothing meaningful changed).** This is the Innovation scoring linchpin. Without it, Telegram is a wrapper (score: 2). With it, the environment is essential (score: 4-5).
5. **Visible triage reasoning in notifications.** The notification doesn't just say "repo X has a problem." It says "I reviewed 47 repos. 3 need your attention. Here's the evidence." The 44-repo silence is a visible decision, not an absence. "I reviewed your estate and chose not to bother you about 44 of them" is a feature announcement. This is what makes the decision-making a user-facing feature, not internal plumbing.
6. Telegram bot: responds to /estate command with a formatted briefing
7. Briefing links to a single-page HTML dashboard showing estate overview + evidence for flagged repos. **Must be mobile-friendly.** The Telegram link opens in a phone browser. If the dashboard breaks on mobile, the demo breaks at the moment it matters most. **The dashboard link is the real action channel:** it's how the user goes from notification to detail.
8. "Deployment evidence detected" language (not "this is deployed"). Facts vs. inference vs. unknowns must be visible. This is a Technical Execution scoring advantage ("thoughtful failure handling").
9. Public GitHub repo with README explaining the build

### STRETCH (build if time allows, high scoring value)

- **/check [repo] Telegram command.** Lets you ask Observator about a specific repo. Makes Telegram a conversation, not a one-way pipe. Lifts Innovation and Usefulness scores. **Confirmed as priority stretch goal.**

### STUB (comment + notes, don't build)

- Scheduled runs via Trigger.dev (demo as manual trigger)
- /brief Telegram command
- **Email action channel.** Notification includes "📧 Detailed report sent to your email." The email body can be generated as a text file alongside the dashboard HTML (same agent output, different format). If time allows, show it in the demo as "here's what would land in your inbox." Signals the multi-channel architecture without wiring SMTP. 15 minutes if built, zero if left as text stub.
- Previous-snapshot comparison (first run vs. second run)
- CopilotKit dashboard copilot
- Private repo support (OAuth complexity)
- Maintain/Preserve/Investigate/Retire decision workflow
- Historical trending
- Multi-provider support (GitLab, Bitbucket)
- Ownership graph
- Real user onboarding (hard-code your own config)

### NEVER

- Modify, archive, or delete any repository
- Pretend GitHub evidence proves external infrastructure is live
- Store credentials beyond the demo session
- Build multi-user auth
- Build the complete Observator PRD
- Send on behalf of the user
- Manufacture alerts when nothing meaningful changed

---

## Demo format: Option C (confirmed)

**Notification + /check follow-up.** Two beats in two minutes.

**Beat 1: The agent comes to you.** Unprompted Telegram notification arrives. It says: "I reviewed 47 repos. 3 need your attention. Here's the evidence." Each finding has a one-line summary, confidence language, and evidence citation. The 44 repos that didn't warrant a notification are quantified, not hidden. At the bottom: a dashboard link and (if built) an email stub line.

**Beat 2: You talk back.** You reply `/check observator-clew` and the agent responds with repo-specific detail: deployment evidence, last activity, open issues, and what it recommends. This proves Telegram is a conversation, not a one-way pipe.

**Beat 3 (if time): The dashboard.** Tap the dashboard link. It opens on the phone, mobile-friendly, showing the full estate at a glance. This is the action channel: notification to detail in one tap.

**Why Option C wins across all four criteria:**

| Criterion | What Option C shows | Score ceiling |
|---|---|---|
| Core Requirements | Agent runs end to end, notification + interactive query + dashboard | 4-5 |
| Innovation | Agent comes to you (not wrapper), you can converse, NO_NOTIFICATION proves environment is essential | 4-5 |
| Technical Execution | GitHub API, agent reasoning, Telegram integration, structured output, confidence language | 4 |
| Usefulness | Context-intelligent, controllable (/check), multi-channel (dashboard link), clear about what it doesn't know | 4-5 |

**The decision-making is the feature, not the plumbing.** The agent's triage (what it chose to surface, what it chose to skip, and why) is visible in every notification. That's the Usefulness score: the user sees the agent exercising judgment, not just pattern-matching.

---

## What to do before Saturday

All of this is allowed under the hackathon rules (data and templates are fine; the agent logic is net-new).

1. **Create the Telegram bot** via BotFather. Get the token. Test sending a message to yourself. Test MarkdownV2 formatting. 15 minutes.
2. **Snapshot your GitHub repos** into a JSON file. Use the GitHub API to pull metadata for all 60+ repos: name, description, last push date, language, archived, has_issues, open_issues_count, homepage, topics, default_branch. Then for each repo, check for the presence of key files (README.md, Dockerfile, vercel.json, package.json, .github/workflows/). Save as `estate-snapshot.json`. 30 minutes.
3. **Set up the repo skeleton.** MIT license, .gitignore, README shell, folder structure, package.json or requirements.txt with known dependencies. 10 minutes.
4. **Get API keys.** OpenAI or OpenRouter API key. GitHub personal access token (for live API stretch goal). Telegram bot token. 10 minutes.
5. **Script the demo video.** Write the exact narration. Know what Telegram will show. Know what the dashboard will show. Know the closing line. The demo script IS the build spec. 20 minutes.
6. **Draft the social media post template.** Tagging event partners is a submission requirement. Have the template ready with blanks for the project link and video. 5 minutes.
7. **Test Trigger.dev account setup** (optional). If you want the sponsor integration, create an account and a project. Don't build anything; just have the account ready. 10 minutes.

---

## The decision

Observator Clew scoped to Telegram + single-page dashboard is the right build for Saturday. The thesis is sharp, the demo is personal, the architecture is sound, and the MUST list is achievable in 4 hours flat with pre-prepped data.

The judging criteria confirm the strategy. The four criteria reward exactly what Observator does well: a working agent in an environment that's essential to the experience (not a wrapper), thoughtful failure handling (unknowns as a feature), and context-intelligent behavior that remains clear and controllable. The NO_NOTIFICATION decision is the single highest-leverage feature for scoring: it's what separates a 2 from a 4-5 on Innovation.

The ChatGPT analysis gets the big things right: agent-not-cron, model authority contract, facts-vs-inference, NO_NOTIFICATION. Where it optimizes, it tends to underestimate integration time (GitHub API, Telegram formatting, Trigger.dev). The revised MUST/STRETCH/STUB/NEVER above accounts for those realities and maps features to scoring impact.

**Priority order if time gets tight:** Visible triage reasoning > /check interaction > dashboard > email stub. Judges score the agent in its environment. The environment is Telegram. The dashboard is the action channel (one tap from notification to detail). The email stub signals multi-channel design without build cost.

**Demo format:** Option C (notification + /check follow-up). See the demo format section above.

One sentence pitch: **An autonomous agent that watches your software estate, gathers evidence about what changed, and only interrupts you in Telegram when something is worth knowing.**

One sentence for the README: **Creating is becoming nearly free. Maintaining never did.**

---

*Prepared: September 10, 2026 (v3: confirmed Option C demo format, visible triage reasoning as MUST, email stub as STUB, dashboard as action channel)*
*AI assisted. Human approved. Powered by NLP.*
