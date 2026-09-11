# Observator Clew --- Hackathon Scope Review

**Purpose:** Synthesize the proposed Telegram-first hackathon scope,
stress-test its assumptions, and define the smallest version of
Observator Clew that still demonstrates a real agent.

**Event constraint:** \~4.25-hour build window\
**Working thesis:** **Creating is becoming nearly free. Maintaining
never did.**\
**Product line:** **Know what still needs you.**

------------------------------------------------------------------------

## 1. Executive Verdict

Claude's recommendation is directionally strong, but I would **not adopt
the scope unchanged**.

The strongest parts are:

-   use the builder's real GitHub estate as the demo;
-   make Telegram the primary surface;
-   keep the web experience extremely small;
-   keep repository facts deterministic;
-   avoid unnecessary sponsor integrations;
-   build read-only;
-   optimize the entire build around a two-minute demo.

The biggest problem is that the proposed scope accidentally removes much
of the **agent** while trying to reduce engineering risk.

If scheduled observation is stubbed, deep investigation is stubbed,
lifecycle reasoning is removed, and the primary demo is the user typing
`/estate`, the result risks becoming:

> **A Telegram bot that summarizes GitHub metadata.**

That is useful automation. It is not the strongest expression of the
hackathon theme.

The better scope is:

> **Observator wakes on a schedule, reviews deterministic changes across
> a GitHub estate, decides which projects warrant investigation, gathers
> additional repository evidence when needed, decides whether anything
> is worth interrupting the user about, and sends a plain-language
> Telegram briefing with a link to the evidence.**

The scheduler is not the agent. It wakes the agent.

Telegram is where the agent shows up.

The linked web page is the receipt.

------------------------------------------------------------------------

## 2. What Claude Got Right

### 2.1 The thesis is unusually well suited to a builder hackathon

The line:

> **Creating is becoming nearly free. Maintaining never did.**

is immediately legible to people who build software quickly.

Using a real, messy GitHub portfolio strengthens the demo because the
product is operating on an actual software estate rather than a
fabricated dashboard dataset.

That does **not** prove market demand. It does prove that the problem is
concrete enough to demonstrate.

### 2.2 Telegram should be the primary surface

This is the right instinct.

Observator should come to the user rather than require the user to
remember to visit another dashboard.

That supports the product thesis and the hackathon theme better than a
conventional web app with a chatbot attached.

### 2.3 The dashboard should not become a second product

Agreed.

For the hackathon, the web surface should be closer to an **evidence
report** than a full application:

-   estate totals;
-   latest observation time;
-   projects surfaced by Observator;
-   plain-language explanation;
-   evidence;
-   unknowns;
-   perhaps the remaining portfolio grouped simply.

No settings system. No complex navigation. No dashboard architecture
project hiding inside the hackathon project.

### 2.4 Deterministic facts belong in code

Strong agreement.

Repository count, last push, archived state, README presence, workflows,
homepage metadata, files, releases, and other directly observable
properties should not be invented or calculated by a model.

The model should reason over evidence, not manufacture the evidence.

### 2.5 Sponsor restraint is correct

Using every sponsor API would weaken the project.

Trigger.dev and one model provider have natural roles. Exa, CopilotKit,
Auth0, and other tools should be excluded unless the product genuinely
needs them.

Sponsor logos are not architecture.

### 2.6 Read-only is the correct safety boundary

Absolutely keep:

-   no repository modification;
-   no archival;
-   no deletion;
-   no credential revocation;
-   no infrastructure mutation.

The hackathon should demonstrate observation and judgment, not
destructive authority.

------------------------------------------------------------------------

## 3. Where I Disagree

### 3.1 Scheduled execution should be MUST, not STUB

Claude proposes stubbing scheduled runs and demonstrating a manual
trigger.

I would reverse that.

The schedule is one of the clearest ways to show that Observator is
**present without being summoned**.

A command-driven interaction:

> `/estate`

makes Observator look like a chatbot or CLI wearing a Telegram costume.

A scheduled message:

> "I checked your estate this morning. Two projects are worth your
> attention."

shows the actual behavior we are trying to build.

The cron is still not the agent. It is simply the trigger that gives the
agent an opportunity to observe and decide.

For the demo, there should also be a manual **Run now** path so nobody
waits for a clock.

### 3.2 Three Telegram commands are unnecessary scope

Claude proposes:

-   `/estate`
-   `/check [repo]`
-   `/brief`

That creates command parsing, conversational states, response
formatting, error paths, and demo choices that do not strengthen the
central story.

For Saturday, Telegram should primarily be an **outbound interruption
surface**.

If one interactive command survives, make it:

> `/check repo-name`

That demonstrates user-directed follow-up without turning Observator
into a general chat interface.

### 3.3 "One LLM one-liner per repo" is the wrong use of AI

Running model reasoning across every repository is unnecessary,
expensive, slower, and conceptually weaker.

It also creates sixty opportunities for the model to confidently narrate
trivial metadata.

Instead:

1.  deterministic code inventories everything;
2.  deterministic code identifies changed or unusual candidates;
3.  the agent reasons deeply over only a small candidate set;
4.  the agent decides what deserves the user's attention.

The model should spend intelligence where interpretation can change a
decision.

### 3.4 `archive-candidate` is too strong for deterministic triage

A repository being old, quiet, unpopular, or issue-heavy does not prove
it should be archived.

This conflicts with a core Observator principle:

> **Inactivity is a signal, not a verdict.**

Deterministic buckets should describe observable state, not prescribe
lifecycle action.

Better internal triage language:

-   recently active;
-   changed since last observation;
-   quiet;
-   long-quiet;
-   deployment evidence detected;
-   scheduled automation detected;
-   insufficient evidence.

Then the agent can interpret those signals.

### 3.5 Removing lifecycle decisions entirely throws away useful differentiation

Claude proposes removing Maintain / Preserve / Investigate / Retire / No
Action.

For the hackathon, implementing a complete lifecycle-management workflow
would indeed be too much.

But eliminating the concept entirely makes Observator much closer to a
GitHub activity digest.

A better compromise is to support only a **recommendation**, not a
workflow.

For example:

> **Recommendation: INVESTIGATE**

or:

> **No action suggested**

No buttons. No state machine. No retirement execution.

This preserves the product's point of view without creating another
subsystem.

### 3.6 A manual Telegram conversation is not the strongest demo story

Claude's suggested demo begins:

> "Open Telegram. Type `/estate`."

That proves the bot responds.

The stronger opening is:

> **Open Telegram. An Observator briefing is already waiting.**

Then explain:

> "I didn't ask it a question. Observator checked my software estate,
> decided two things were worth my attention, and came to me."

That is much closer to the event's "agent everywhere" premise.

------------------------------------------------------------------------

## 4. Assumption Audit

The following claims should be treated as hypotheses, not facts.

### Assumption A: "The thesis is a hackathon weapon."

**What supports it:** Builders are likely to understand repository
accumulation and maintenance burden quickly.

**What does not follow:** A memorable line does not prove judges will
value the problem, that the product is differentiated, or that users
will pay.

**Verdict:** Strong pitch hypothesis. Unproven competitive advantage.

### Assumption B: "You are the target user, therefore the problem is validated."

**Refutation:** Being an authentic target user makes the demo credible.
It does not validate a market. One person's sixty repositories could be
an unusual working style rather than a broad paid problem.

**What Saturday can prove:** The workflow produces a useful decision on
a real estate.

**What Saturday cannot prove:** Market size, retention, willingness to
pay, or repeatability across builders.

### Assumption C: "Telegram fits the theme perfectly."

**Refutation:** Telegram fits the *surface* requirement well, but simply
placing a bot in Telegram does not make the product meaningfully
agentic.

**Requirement:** The system should initiate, investigate, decide, or
adapt based on context rather than merely wait for commands.

### Assumption D: "Two surfaces are one too many."

**Refutation:** This depends on what "dashboard" means.

A second interactive application with auth, state, filtering, routing,
and actions is too much.

A generated read-only evidence page is not meaningfully the same
engineering burden.

**Verdict:** Reject a full dashboard. Keep a tiny evidence page.

### Assumption E: "Five integration points means two will be half-baked."

**Refutation:** Integration count alone is a poor complexity measure.

A Telegram send API and a scheduled Trigger.dev task can be simpler than
one OAuth flow.

The real risks are:

-   authentication;
-   deployment;
-   external API reliability;
-   state persistence;
-   model latency;
-   unfamiliar SDKs.

**Verdict:** Budget by failure modes, not logo count.

### Assumption F: "The triage engine can bucket repos as archive candidates."

**Refutation:** Metadata can identify inactivity. It cannot establish
that archival is appropriate.

A stable library, finished reference project, deployed utility, or
historical artifact can all be quiet for legitimate reasons.

**Verdict:** Deterministic triage should describe evidence. Lifecycle
interpretation belongs later.

### Assumption G: "Open issues are a useful universal maintenance signal."

**Refutation:** Sometimes. Many repositories disable issues, never use
them, use another tracker, or intentionally leave issues open.

**Verdict:** Treat issue count as weak contextual evidence, not a health
score.

### Assumption H: "Stars and forks matter to the user's ownership decision."

**Refutation:** Usually weakly.

A zero-star private utility may matter enormously. A highly starred
abandoned experiment may create no ongoing burden.

**Verdict:** Collect if cheap, but do not prioritize them in V1
reasoning.

### Assumption I: "An LLM one-liner per repo adds value."

**Refutation:** It risks converting metadata into prose without adding
judgment.

> "Last touched 14 months ago and has three open issues."

is mostly a sentence-shaped database row.

**Verdict:** Use the model only on candidates where interpretation
matters.

### Assumption J: "Manual Trigger.dev execution still demonstrates the scheduled-agent idea."

**Refutation:** It demonstrates the workflow but weakens the product
behavior.

**Verdict:** Implement the real schedule if possible, plus a manual run
path for the demo.

### Assumption K: "A static page is enough for the dashboard."

**Mostly supported for the hackathon.**

The page needs only to substantiate the Telegram briefing.

It does not need to prove the eventual product UX.

### Assumption L: "Using a sponsor tool is a strategic advantage."

**Unknown.**

Sponsor integration may matter for sponsor-specific judging or prizes,
but forced integrations can also make the build worse.

**Verdict:** Use Trigger.dev because scheduling belongs in the
architecture. Choose the model provider because reasoning belongs in the
architecture. Stop there unless new event information justifies another
tool.

### Assumption M: "OpenRouter model swapping is useful to demonstrate."

**Refutation:** Model swapping does not strengthen the Observator story
unless model comparison is itself relevant.

**Verdict:** Pick one reliable model and spend demo time on the product.

### Assumption N: "Google Cloud Run should host the summary page."

**Refutation:** Only if it is already the fastest deployment path on
build day or materially helps a sponsor category.

Infrastructure novelty is not part of the product.

**Verdict:** Use the deployment path with the lowest failure
probability.

### Assumption O: "Preparing a JSON snapshot is definitely allowed."

**Caution:** The event recap says existing data/templates are allowed
while core functionality must be net-new. A repository snapshot appears
consistent with that summary, but the final event rules should govern.

**Verdict:** Use the snapshot as fallback/test data, and clearly
disclose what was prepared before the event.

### Assumption P: "A repo skeleton can be prepared in advance."

**Caution:** Same issue. The recap says templates/starter components may
be used, but the exact boundary between a generic starter and
project-specific implementation should be respected.

**Verdict:** Prefer a generic starter if permitted and document
pre-existing material.

### Assumption Q: "Solo is stronger because the estate is personal."

**Refutation:** The personal story is stronger solo, but team
composition is an execution decision.

A teammate could reduce integration risk or improve demo polish.
Coordination could also consume the build window.

**Verdict:** No universal answer. Optimize for known working rhythm and
role clarity.

### Assumption R: "No write access means no guessing."

**Refutation:** These are unrelated.

Read-only access limits destructive capability. It does not prevent
inference or hallucination.

**Verdict:** The correct pair is:

> **Read-only. Evidence-backed. Unknowns stay unknown.**

### Assumption S: "Every finding has a receipt."

**Requirement, not current fact.**

This is only true if the implementation preserves source evidence and
the UI exposes it.

**Verdict:** Make this an acceptance criterion.

### Assumption T: "The agent should notify every day."

**Refutation:** Daily execution does not require daily notification.

A stewardship agent that sends noise every morning becomes another
chore.

**Verdict:** Run daily if desired. Notify only when the agent decides
something is worth the interruption. A weekly digest can summarize the
quiet periods.

------------------------------------------------------------------------

## 5. Recommended Hackathon Product

### One-sentence definition

**Observator Clew is a read-only agent that watches your GitHub estate,
investigates changes that may matter, and tells you in Telegram only
when something deserves your attention.**

### The user experience

``` text
Trigger.dev schedule / manual demo trigger
                    │
                    ▼
          Deterministic estate scan
                    │
                    ▼
              Candidate triage
                    │
                    ▼
             OBSERVATOR AGENT
                    │
          ┌─────────┴─────────┐
          │                   │
   Need more evidence?        No
          │                   │
          ▼                   │
   Read relevant GitHub       │
   files / metadata           │
          │                   │
          └─────────┬─────────┘
                    ▼
        Interpret evidence + unknowns
                    │
                    ▼
          Is interruption warranted?
              │               │
             NO              YES
              │               │
              ▼               ▼
        Record quiet run   Telegram brief
                                  │
                                  ▼
                         Evidence report page
```

This gives the agent an actual decision boundary.

------------------------------------------------------------------------

## 6. Agent Authority Contract

The model has exactly three jobs.

### Job 1 --- Investigation choice

Given deterministic candidate signals, decide which candidates need
additional repository evidence before a useful conclusion can be made.

### Job 2 --- Evidence interpretation

Interpret verified evidence and explicitly identified unknowns in the
context of whether the project appears to need attention.

### Job 3 --- Interruption decision and explanation

Decide whether the evidence is consequential enough to interrupt the
user and, if so, explain why in plain language.

### The model does not decide facts

Code establishes:

-   repository identity;
-   dates;
-   commit/activity metadata;
-   archive state;
-   README presence;
-   workflow presence;
-   scheduled workflow presence;
-   releases;
-   configuration-file presence;
-   homepage metadata;
-   detected deployment configuration;
-   previous snapshot;
-   changes since previous snapshot.

### Required reasoning shape

``` text
FACTS
→ UNKNOWNS
→ INTERPRETATION
→ RECOMMENDATION
→ NOTIFY / DO NOT NOTIFY
```

Never:

``` text
OLD REPO
→ "ABANDONED"
→ RED BADGE
```

------------------------------------------------------------------------

## 7. Revised MUST / STUB / NEVER

### MUST

-   Read a real GitHub estate.
-   Collect deterministic repository evidence.
-   Persist or load a previous observation so "what changed" is real.
-   Rank candidates before model reasoning.
-   Let the agent investigate a small candidate set.
-   Distinguish facts, inference, and unknowns.
-   Let the agent choose **NOTIFY** or **NO_NOTIFICATION**.
-   Send a Telegram briefing when notification is warranted.
-   Support a manual run for the live demo.
-   Implement a real scheduled trigger if the chosen scheduler can be
    wired reliably.
-   Link to one read-only evidence page.
-   Show the receipt behind at least one surfaced finding.
-   Remain read-only.

### STUB

-   Full user onboarding.
-   Multi-user accounts.
-   GitLab/Bitbucket.
-   External cloud/deployment-provider verification.
-   Historical trend charts.
-   Ownership graph.
-   Cost analysis.
-   Full lifecycle workflows.
-   Retirement execution.
-   General conversational Telegram assistant.
-   Rich dashboard interactions.

### NEVER

-   Delete infrastructure.
-   Modify repository content.
-   Archive repositories.
-   Revoke credentials.
-   Claim an external deployment is live based only on repository
    configuration.
-   Treat inactivity as proof of abandonment.
-   Generate findings merely to make the demo look busy.
-   Send repository secrets or credentials to the model.
-   Build integrations solely to collect sponsor logos.

------------------------------------------------------------------------

## 8. Minimal Telegram Behavior

### Scheduled briefing

``` text
OBSERVATOR CLEW

I checked 60 repositories.

Two are worth your attention this week.

old-hackathon-app
INVESTIGATE

Quiet for 184 days.
Deployment configuration is still present.
The README describes it as a hackathon prototype.

Unknown:
I cannot verify from GitHub whether the deployment is still live.

Why this surfaced →
[View evidence]

Everything else:
No new attention needed.
```

### Quiet run

A quiet run should be a legitimate result:

``` text
NO_NOTIFICATION
```

For a weekly recap, that can become:

``` text
I checked your estate this week.
Nothing changed enough to need your attention.
```

That is a feature, not a failed demo.

------------------------------------------------------------------------

## 9. Minimal Evidence Page

The web page should answer four questions:

1.  **What did Observator notice?**
2.  **Why does it think this matters?**
3.  **What evidence supports that?**
4.  **What does it still not know?**

Suggested structure:

``` text
OBSERVATOR CLEW
Know what still needs you.

60 projects observed
2 worth attention
Last observation: 9:04 AM

NEEDS ATTENTION

old-hackathon-app
Recommendation: INVESTIGATE

Why
This project has been quiet for six months and still
contains deployment configuration.

Evidence
✓ Last meaningful repository activity: [date]
✓ Repository is not archived
✓ Deployment configuration detected
✓ README describes it as a hackathon prototype

Unknown
? Is the deployment currently live?
? Does it contain data or active users?

[GitHub evidence links]
```

No charts are required to prove the product.

------------------------------------------------------------------------

### Mobile-first requirement

The Estate Overview must be **mobile-friendly**. Telegram is the primary
notification surface, so users will naturally tap **View evidence** from a
phone. Design and test the linked page for a narrow mobile viewport first.

For the hackathon, use a single-column responsive layout, readable typography,
large tap targets, and evidence/unknown sections that stack cleanly. Avoid
horizontal-scrolling tables and interactions that depend on desktop width.

**Acceptance check:** open the Telegram briefing on a phone, tap the evidence
link, and understand the finding without rotating the device or zooming.

---

## 10. Recommended Two-Minute Demo

### 0:00--0:20 --- Problem

> "AI has made it incredibly cheap for me to create software. My GitHub
> now has around sixty repositories, and creating them was the easy
> part. Remembering what still needs me isn't."

### 0:20--0:40 --- Presence

Open Telegram.

A briefing from Observator is already waiting.

> "I didn't ask it a question. Observator wakes up, checks my software
> estate, and decides whether anything is worth interrupting me about."

### 0:40--1:10 --- Agent behavior

Show the surfaced project.

Explain:

-   deterministic scan found the candidate;
-   Observator needed more context;
-   it inspected repository evidence;
-   it separated facts from unknowns;
-   it decided this project warranted attention.

### 1:10--1:35 --- Receipt

Tap the evidence link.

Show:

-   recommendation;
-   evidence;
-   unknowns;
-   source links.

> "GitHub can show evidence that a deployment was configured. It cannot
> prove the deployment is still alive, so Observator says that instead
> of guessing."

### 1:35--1:55 --- Agent boundary

> "It has no write access. It cannot archive a repo or delete anything.
> And it is not rewarded for finding a problem every day. If nothing
> needs me, it stays quiet."

### 1:55--2:00 --- Close

> **"Creating is becoming nearly free. Maintaining never did."**

------------------------------------------------------------------------

## 11. Build-Order Recommendation

The build should proceed in vertical slices.

### Block 1 --- Evidence

GitHub → deterministic estate JSON.

**PASS:** Real repository facts can be inspected locally.

### Block 2 --- Triage

Estate JSON → small candidate list.

**PASS:** The system can explain deterministically why each candidate
was selected.

### Block 3 --- Agent

Candidate → optional evidence retrieval → interpretation → `NOTIFY` /
`NO_NOTIFICATION`.

**PASS:** Agent output distinguishes facts, unknowns, interpretation,
and recommendation.

### Block 4 --- Telegram

Agent result → Telegram briefing.

**PASS:** Real message arrives with correct evidence and no invented
claims.

### Block 5 --- Receipt

Briefing → evidence URL.

**PASS:** Link opens a simple page supporting the claim made in
Telegram.

### Block 6 --- Schedule

Scheduler → same tested workflow.

**PASS:** Scheduled invocation produces the same behavior as manual
invocation.

### Block 7 --- Demo hardening

Fallback snapshot, deterministic demo candidate, README, disclosure,
video capture.

**PASS:** The demo survives an API hiccup without pretending the
fallback is live data.

------------------------------------------------------------------------

## 12. Cut Order if Time Collapses

Cut features in this order:

1.  `/check` interactive Telegram command.
2.  Portfolio-wide web breakdown.
3.  Weekly/daily preference UI.
4.  Fancy formatting.
5.  Historical statistics beyond one previous snapshot.
6.  Automatic schedule configuration UI.

Do **not** cut:

1.  evidence;
2.  agent investigation;
3.  interruption decision;
4.  Telegram delivery;
5.  the distinction between fact and unknown.

Those five pieces are the demonstration.

------------------------------------------------------------------------

## 13. Strengths of This Scope

-   Extremely personal demo with real data.
-   Clear hackathon theme fit.
-   Small enough to explain in two minutes.
-   Agent behavior is visible and defensible.
-   Deterministic/AI boundary is technically credible.
-   Read-only architecture limits blast radius.
-   Telegram creates genuine ambient presence.
-   Evidence page supports the "receipt" philosophy.
-   `NO_NOTIFICATION` prevents an anxiety-machine design.
-   The prototype is a legitimate vertical slice of the larger
    Observator PRD.

------------------------------------------------------------------------

## 14. Weaknesses and Risks

### GitHub is not the software estate

The prototype can infer deployment evidence but cannot establish
external operational truth.

This must be presented as a limitation, not hidden.

### One previous snapshot is thin history

It is enough to demonstrate change detection but not enough to establish
trends.

### The agent boundary may be challenged

A judge may reasonably ask whether deterministic triage plus an LLM
summary is really an agent.

The answer must be visible in the implementation: the agent chooses
whether to investigate further and whether to interrupt.

### Telegram may be perceived as "just a bot"

Again, proactive behavior matters.

A scheduled autonomous briefing is stronger than a command-response
demo.

### Personal relevance does not equal market validation

The demo proves usefulness for one real software estate.

It does not prove a company.

### Four hours is still four hours

GitHub, Telegram, scheduling, model calls, persistence, hosting, and
deployment can each fail for boring reasons.

The fallback path should be designed before the build begins.

------------------------------------------------------------------------

## 15. Final Recommendation

Build **Telegram-first Observator**, but do not reduce it to a Telegram
command bot.

The hackathon version should demonstrate one complete autonomous loop:

> **Wake → Observe → Triage → Investigate → Reason → Decide whether to
> interrupt → Notify → Show evidence.**

The minimum viable agent is not the dashboard.

It is not the cron.

It is not the LLM.

It is the **decision-making loop connecting them**.

The dashboard can be tiny.

The scheduler can be simple.

The model can have only three jobs.

But the agent must visibly make a decision that deterministic automation
alone did not already make.

That is the version worth building Saturday.

------------------------------------------------------------------------

## 16. Working Hackathon Pitch

> **I have around sixty GitHub repositories. AI made creating them
> cheap, but keeping track of what still needs me did not get cheaper.
> Observator Clew is a read-only agent that watches my GitHub estate. It
> wakes up on a schedule, finds changes worth investigating, gathers the
> evidence it needs, and decides whether something is important enough
> to interrupt me about in Telegram. If I want to know why, every alert
> links back to the evidence and the things Observator still doesn't
> know. Creating is becoming nearly free. Maintaining never did.**
