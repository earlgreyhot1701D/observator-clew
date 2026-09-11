# AI Tinkerers "Agents, Everywhere" Hackathon — Full Recap

**Event:** Agents, Everywhere: Bots, Channels, & More — Global Hackathon
**Host:** AI Tinkerers, Los Angeles chapter
**Date:** Saturday, September 12, 2026
**Time:** 10:00 AM – 5:00 PM PDT
**Location:** In-person, Los Angeles (exact venue in handbook)
**Status:** Accepted

---

## The Theme

Agents are leaving the chatbox. Build an agent for a place people already work, talk, or live, then make it meaningfully more useful because of that context. Put it into the web, mobile, Slack, Teams, messaging, browsers, voice, wearables, robotics, or somewhere nobody expects to find one yet. What becomes possible when the agent shows up where the work is already happening?

The goal is a working prototype that can be demonstrated by the end of the day. Keep the scope tight, prioritize the core interaction, and make sure the agent's environment is essential to the experience. Any technical stack is allowed.

---

## Schedule and Build Window

| Time (PDT) | What |
|---|---|
| 10:00 – 10:30 AM | Arrive, check in, grab food, meet other builders |
| 10:30 – 11:00 AM | Global opening broadcast, challenge briefing, starter-kit walkthrough |
| 11:00 – 11:15 AM | Form teams and finalize project ideas |
| 11:15 AM – 3:30 PM | **Build window (~4.25 hours)** |
| 3:30 – 4:00 PM | Complete project submissions in the portal |
| 4:00 – 4:45 PM | Optional local show-and-tell (after submitting) |
| 4:45 – 5:00 PM | Wrap and group photo |

That build window is tight. 4 hours and 15 minutes from "go" to submissions due. Note: submissions close at 3:30, then the optional show-and-tell happens AFTER you've already submitted. No local judging. All projects enter the same global competition.

---

## Submission Requirements

Every submission needs all five:

1. **Title** for the project
2. **Written description** of what it does and why
3. **Public GitHub repo** with source code
4. **2-minute demo video** (hard cap)
5. **Social media post** tagging event partners

---

## Judging Criteria

Projects are evaluated globally after submissions close. Judges score every project from 1 to 5 across four criteria. This is the scorecard. Build to it.

### 1. Core Requirements & Functionality

Does the project deliver a working agent inside a place where people already work, talk, or live? Does the core workflow function end to end?

| Score | What it means |
|---|---|
| 1 | Does not run or does not demonstrate a functional agent |
| 2 | Parts run, but core workflow or environment integration is incomplete |
| 3 | Basic end-to-end agent works in the intended environment, with limitations or bugs |
| 4 | Works reliably, complete agent experience with only minor issues |
| 5 | Robust, reliable, and fully functional within its intended environment |

**What this means for us:** The agent must work end to end. A broken demo is a 1 or 2. A working demo with rough edges is a 3. Finishing matters more than features.

### 2. Innovation & Theme Alignment

Does the project explore a compelling new place or interaction for agents? Does the environment materially improve what the agent can do?

| Score | What it means |
|---|---|
| 1 | Generic chatbot or automation; the selected environment is irrelevant |
| 2 | Agent appears in an eligible environment, but the environment is mostly a wrapper |
| 3 | Clearly addresses the theme, environment adds meaningful value |
| 4 | Environment shapes the core workflow and enables an original agent experience |
| 5 | Reveals a surprising new agent pattern whose central value could not be reproduced in a standalone chatbox |

**What this means for us:** The environment (Telegram) cannot be a wrapper. Observator in Telegram must be materially different from Observator as a web app. The notification-as-interruption model and the "is this worth bothering you about?" decision are what make Telegram essential, not decorative. Aim for 4-5 here.

### 3. Technical Execution & Integration

Consider the code, architecture, reliability, tool use, data handling, and depth of integration with the selected environment.

| Score | What it means |
|---|---|
| 1 | Little or no technical execution; primarily conceptual or mocked |
| 2 | Basic, unstable, or superficial integrations |
| 3 | Solid technical execution and working integrations, some rough edges |
| 4 | Well engineered, reliable, integrates tools/data/environment effectively |
| 5 | Exceptional engineering, robust orchestration, thoughtful failure handling, deeply integrated architecture |

**What this means for us:** The deterministic-first architecture, model authority contract, and evidence-backed findings pattern ARE the technical story. Thoughtful failure handling = "Observator cannot verify from GitHub alone whether this deployment remains active." That's a 4-5 answer to a question most hackathon projects ignore.

### 4. Usefulness & Agentic Experience

Does the project create clear value for its intended users? Is the agent intuitive, effective, and appropriate for the environment?

| Score | What it means |
|---|---|
| 1 | Use case unclear, agent provides little meaningful value |
| 2 | Recognizable use case, but agent's contribution is limited or resembles basic prompt-and-response |
| 3 | Useful, understandable, agent performs meaningful actions with reasonable user control |
| 4 | Solves a clear problem, agent feels native to environment, strong human-AI interaction |
| 5 | Unlocks substantial value through agent experience designed specifically for its environment, uses context intelligently while remaining clear and controllable |

**What this means for us:** "Uses context intelligently while remaining clear and controllable." That's the whole Observator pitch. The agent uses YOUR GitHub context. It's clear (evidence-backed findings, no hallucinated claims). It's controllable (read-only, you decide what to do). And the "designed specifically for its environment" piece means the Telegram interruption model and the dashboard evidence trail must feel intentional, not bolted on. Aim for 4-5.

---

## Build Eligibility Rules

The build must be **net-new**, created during the official hackathon period. You can use existing templates, reusable components, libraries, prompts, starter code, and other building blocks, but the project and its core functionality must be built during the event. A pre-existing project cannot be resubmitted or extended and entered as a new hackathon project. Teams must be prepared to explain which parts were created during the hackathon versus what existed before.

What transfers freely: domain knowledge, build philosophy, design patterns, lessons learned, mock data, starter templates. What doesn't: prior codebases. Porch Light code cannot be submitted here. The Observator Clew PRD is a concept doc, not code. The idea muscle and domain expertise absolutely transfer.

---

## Prizes and Credits

Global prizes and partner awards will be announced before September 12. Not yet published as of September 10.

Every accepted builder receives access to a package of credits and offers from participating partners. Redemption instructions and the complete package will be posted before build day.

---

## Team Status

Solo or team. No team formed yet. The portal has a "Browse Teams" feature (5 teams listed as of September 10). Decision needed before September 12.

---

## Sponsors

These are the companies providing tools, APIs, and potentially prizes:

- **OpenAI** (marquee sponsor)
- **CopilotKit** — open-source framework for building AI copilots into apps
- **OpenRouter** — unified API across multiple LLM providers
- **Exa** — AI-native search API (semantic search over the web)
- **Auth0** — authentication and identity
- **Ambiguous AI**
- **Trigger.dev** — background jobs and workflow orchestration
- **Mozilla**
- **Google Cloud Run** — serverless container deployment

Using a sponsor's tool or API is a strategic advantage. It signals engagement with the ecosystem and may factor into sponsor-specific prizes. A shared starter repository, sponsor resources, credits, and technical documentation will be added to the portal before build day.

---

## Shara's Profile and Positioning

### What she brings to the room

Court, county, and appellate operations since 2015. Subject matter expertise in public systems that nobody else in a hackathon room typically has. Self-taught AI builder since July 2025 with a track record that speaks:

- **Four hackathon wins** across team and solo formats
- **DoraHacks AWS Global Vibe winner** (Janus Clew, Draper University scholarship)
- **4th of 250** at Devpost AI Vibe Coding Hackathon (Memoria Clew, two category wins)
- **AWS 10,000 AIdeas semifinalist**
- **Speaker, NACM 2026 Midyear Conference** (Albuquerque) on frontline staff leading AI adoption
- **Speaker, LA Superior Court** (July 2026), tailored version of the NACM presentation
- 60 public GitHub repos, 39 dev.to articles documenting builds, failures, and the non-traditional path
- **AWS AI/ML Udacity Scholar** (in progress)
- Currently building Porch Light for the AWS Agents for Humans hackathon

### Build philosophy (the stuff that wins)

- PRD-first, always. Architecture doc before code.
- MUST / STUB / NEVER labels on features
- One file, one responsibility
- Mock data first, then wire APIs
- Block-by-block with PASS/FAIL checkpoints after each block
- Staged prompts: propose first, approve, then implement
- Deterministic structure + AI reasoning at the edges
- Model authority contracts: the model has exactly N jobs, everything else is code
- Verify claims against actual files, not memory

### Stack

AWS (Bedrock, Amplify, Lambda, AgentCore), Next.js, React, Python, Supabase, Vercel. Google stack also proven (Charitas Clew on Cloud Run + Firebase).

### The differentiator nobody else has

Court operations experience inside a public institution that publishes a lot of information correctly. "Publishing correctly and reaching someone are different problems, and the second one almost never gets an owner." That gap between public information and public understanding is the lane.

---

## Current Build: Porch Light

Porch Light is what's on the workbench right now, for the separate AWS Agents for Humans hackathon (deadline Sep 14, 2026). It's relevant here because the domain knowledge, the build patterns, and the lessons transfer directly, even though the code doesn't.

### What it does

City council agendas are public, findable, and unreadable. Three agents work together to watch Ventura's public meeting agendas every week and tell you what changed, in plain English and Spanish, with a receipt on every claim. If you want to comment, it helps you draft one. You write the position. You send it. The agent has no send capability.

### The three agents

1. **Hunter** — finds and fetches new agenda documents
2. **Extractor** — breaks agendas into individual items, rewrites staff language into plain English and Spanish
3. **Watcher** — monitors on behalf of a specific person, matches items against their watchlist

### Stack

Python, AWS Strands Agents SDK v1.53.0, Bedrock AgentCore, Aurora PostgreSQL + pgvector, Vercel (frontend), EventBridge (scheduling).

### Key finding: the guard taught the model what to write

The part of Porch Light that decides whether an agenda item matches your question is an agent running Amazon Nova Lite. When required to include a `matched_terms` field, the model filled it in even on non-matches. The truth was in the reason field, not the terms field. The guard didn't stop the behavior. It taught the model what shape a valid match looked like.

Takeaway: a check on a model's output is itself an input to the model. If the check is legible in the output format, you've described the target, not constrained the behavior. This is the kind of build lesson that transfers to any agent build at this hackathon.

### Model authority contract (from Porch Light)

The model has exactly 3 jobs:
1. Rewrite staff language into plain English (English and Spanish)
2. Decide whether an item is relevant to a named person's watchlist
3. Assemble the structure of a public comment draft (never its stance)

Everything else is deterministic code. Dates, deadlines, item numbers, page ranges, body names, URLs: never model-generated. The verifier is code, not a model. Six checks on every rewrite.

---

## Approved Application Copy

All sections submitted and accepted.

### Biography (786 / 800 characters)

> I'm La Shara Cordero. I've worked in California court, county, and appellate operations since 2015. The last year I've been building on my own time with AWS, Next.js, and React, using what I know to look at challenges, solve problems, and find new ways to address them. I write about the build process, the failures, and the parts nobody warns you about on dev.to. I'm in the AWS AI/ML Udacity Scholarship program to strengthen my foundations. I spoke at the National Association for Court Management 2026 conference on frontline staff leading AI adoption without waiting for permission. I learned in the margins of a full-time job, and I'm still closing gaps. AI assisted. Human approved. Powered by NLP.

### Projects (478 / 500 characters)

> City council agendas are public, findable, and unreadable. I'm building Porch Light: three agents that work together to watch Ventura's public meeting agendas every week and tell you what changed, in plain English and Spanish, with a receipt on every claim. If you want to comment, it helps you draft one. Built with Python, AWS Strands Agents SDK, Bedrock AgentCore, Aurora PostgreSQL, and Vercel. Currently mid-build for the AWS Agents for Humans hackathon, Good Neighbor track.

### Skills (488 / 500 characters)

> Court, county, and appellate operations since 2015. I build with that subject matter expertise on my own time. Four hackathon wins across team and solo formats, including a DoraHacks AWS global win and 4th of 250 at the Devpost AI Vibe Coding Hackathon. AWS 10,000 AIdeas semifinalist. I've spoken at the 2026 National Association for Court Management conference and at the Los Angeles Superior Court on frontline AI adoption. I write about builds, failures, and the non-traditional path on dev.to. Currently in the AWS AI/ML Udacity Scholarship program.

### Startup (484 / 500 characters)

> Clew Labs isn't a startup. It's how I ship. A solo builder practice focused on auditable AI for complex public systems. Every project follows the same rule: structure before intelligence. The model retrieves and prepares, the human decides. I build tools that make evidence, decisions, and unknowns easier to inspect. The suite spans civic readiness tools, agent accountability scanners, and plain-language public record surfaces. All open source, all deployed, all documented on dev.to.

### Areas of Interest (499 / 500 characters)

> I can take an idea from zero to deployed and documented. Where I'm looking to grow is what happens after that: product launch, user acquisition, and sustaining something beyond the hackathon window. I'd love to connect with people who think about go-to-market, community building around a product, or the ops side of keeping a tool alive. I'm also interested in collaborators working on civic tech, public sector AI, or agent design for high-stakes environments where trust and transparency are non-negotiable.

### Investing (79 characters)

> I'm not currently investing or advising startups. I'm here to build and learn.

---

## Voice and Tone Rules (for the build day)

These matter for the demo video, the README, the description, and any pitch. Pulled from Shara's actual writing across 39 dev.to articles:

- First person, conversational, warm and sharp
- Discovery-led: leads with friction not credentials, frames building as discovery not achievement
- No em dashes
- No AI cliches: delve, landscape, straightforward, genuinely, honestly, soapbox phrasing
- Don't count things as identity ("20+ projects" is a counting stat, not about you)
- No absolutes ("I know how" implies knowing everything)
- Pick a lane, don't hedge ("wins or placements" — pick one)
- Honest over optimistic. Limitations language is a feature, not a weakness.
- Opinions stated directly, not as declarations of fact

---

## Competitive Landscape

AI Tinkerers attracts trained engineers. The FAQ explicitly welcomes "the new generation rolling up your sleeves." The differentiator isn't matching their engineering depth. It's bringing domain expertise nobody else in the room has, plus a build track record that proves the work ships.

The winning archetype across hackathons Shara has studied and competed in: **take something invisible and make it inspectable.** Janus Clew, Memoria Clew, Themis Lex, Porch Light. That thread is the Clew.

---

## Agent Ideas for September 12

The constraint: net-new, buildable in ~4.25 hours, must live where people already work/talk/live (not a chatbox). Porch Light domain knowledge transfers. Sponsor tools are available.

### Direction 1: Civic Agent in a Channel

**What:** A Slack/Discord bot (or SMS agent) that watches a public data source (city agendas, permit filings, zoning changes, school board minutes) and pushes plain-language alerts to a channel when something matches what the group cares about.

**Why it fits:** The theme is literally "agents in places people already are." A neighborhood association's Slack channel is where they already coordinate. The agent brings the public record to them instead of making them go find it.

**Sponsor angle:** CopilotKit for the copilot layer, Exa for semantic search over public documents, Google Cloud Run for the backend, Trigger.dev for scheduled monitoring jobs.

**Build feasibility:** Mock data first (pre-scraped agenda items), wire the channel integration, build the matching logic. 4 hours is tight but doable if the data is prepped.

**Differentiator:** Nobody else in the room builds civic agents. The domain expertise is the moat.

### Direction 2: Browser Extension That Reads What You're Looking At

**What:** A browser extension that detects when you're on a government website (city council page, permit portal, court docket) and offers a plain-language overlay: "Here's what this page actually says, here's the deadline, here's what you can do about it."

**Why it fits:** The browser is where people already are. The extension lives in the tab, not in a separate app.

**Sponsor angle:** Mozilla is a sponsor, and a browser extension for civic literacy aligns with their mission. OpenAI or OpenRouter for the language model. Auth0 if there's a saved-preferences layer.

**Build feasibility:** Browser extensions have boilerplate. The hard part is the parsing logic for messy government HTML. Scoping to one city or one document type keeps it buildable.

**Risk:** Browser extensions can be fiddly to demo. The 2-minute video has to show it working live.

### Direction 3: Voice Agent for Public Meetings

**What:** A voice-first agent (phone call or smart speaker) that answers plain-language questions about upcoming public meetings. "Is there anything about my street on the agenda this week?" and it answers in conversational English or Spanish.

**Why it fits:** Voice is a surface people use. Phone calls reach people who don't use Slack or browse city websites. The theme says "wearables, voice, or somewhere unexpected."

**Sponsor angle:** OpenAI (voice/Whisper), Google Cloud Run for hosting.

**Build feasibility:** Voice adds complexity. Telephony integration (Twilio) is doable but adds a layer. Scoping to a smart speaker skill or a simple voice UI might be more realistic for 4 hours.

**Risk:** Voice demos are hard in noisy rooms. Backup: screen-record the voice interaction.

### Direction 4: Meeting Prep Agent in Email/Calendar

**What:** An agent that scans your calendar for upcoming meetings, pulls relevant context from connected sources (agenda docs, prior meeting notes, shared docs), and drops a prep briefing into your inbox or calendar event 30 minutes before.

**Why it fits:** Email and calendar are where people already live. The agent brings context to the meeting, not after it.

**Sponsor angle:** OpenAI or OpenRouter for summarization, Trigger.dev for the scheduled trigger, Auth0 for OAuth to calendar/email.

**Build feasibility:** Calendar and email APIs are well-documented. The risk is OAuth setup eating build time. Mock data first, wire APIs second.

**Differentiator:** Less unique than the civic angle. Meeting prep agents are a crowded category. Would need a sharp hook (e.g., specifically for public sector / government meetings where the prep materials are public records nobody reads).

### Direction 5: Sponsor-Driven Build (Decide on Site)

**What:** Wait until the day, see what the sponsors are offering in terms of APIs, challenges, and prizes, and build around whichever sponsor tool creates the best opportunity.

**Why it fits:** Some hackathons reveal sponsor challenges or bonus prizes day-of. Being flexible lets you pick the thinnest lane.

**Risk:** No pre-planning means the 4.25 hours are even tighter. Mitigated by having the build philosophy, the domain expertise, and the voice rules already locked in. You're not starting from zero on process, just on the specific idea.

---

## Strategic Recommendations

**Decision: Observator Clew, scoped to Telegram + single-page dashboard.**

See `observator-clew-hackathon-review.md` for the full scoping analysis, MUST/STUB/NEVER breakdown, risk matrix, and pre-build checklist.

1. **Observator Clew is the build.** An autonomous agent that watches your software estate on GitHub, gathers evidence about what changed, and only interrupts you in Telegram when something is worth knowing. Dashboard shows the evidence. Thesis: "Creating is becoming nearly free. Maintaining never did."

2. **Build to the judging criteria.** Four criteria, each scored 1-5. The strongest plays for Observator against the scorecard: Core Requirements (working end-to-end Telegram agent), Innovation (Telegram is essential, not a wrapper, because the agent decides whether to interrupt), Technical Execution (deterministic-first architecture, evidence-backed findings, model authority contract), Usefulness (uses YOUR GitHub context intelligently, remains clear and controllable).

3. **Prep mock data before Saturday.** Snapshot your GitHub repos into JSON. The agent logic is net-new; the data isn't. This is explicitly allowed.

4. **Script the demo video before building.** The 2-minute video is a submission requirement. Script it backwards from the Telegram message. Know what you're recording before you write a line of code.

5. **Solo.** The "this is MY estate" angle is the entire pitch. A teammate doesn't add to that story. The domain knowledge is yours. The repo graveyard is yours.

---

## Pre-Build Checklist

- [ ] Decide on agent idea (Direction 1–5 or something new)
- [ ] Decide solo or team
- [ ] Prep mock data (if civic direction)
- [ ] Set up repo skeleton (MIT license, README, .gitignore, disclosure if needed)
- [ ] Pick sponsor tools to integrate
- [ ] Script the 2-minute demo video
- [ ] Draft the social media post template (tagging event partners)
- [ ] Review sponsor APIs and get keys/accounts set up
- [ ] Charge laptop, prep dev environment, test deploys

---

## Key Links

- AI Tinkerers LA: https://la.aitinkerers.org
- Hackathon portal: https://la.aitinkerers.org/hackathons/h_6xwsooXcdbo
- Handbook: https://la.aitinkerers.org/hackathons/h_6xwsooXcdbo (Handbook tab in portal)
- GitHub: https://github.com/earlgreyhot1701D
- dev.to: https://dev.to/earlgreyhot1701d
- Clew Labs portfolio: https://earlgreyhot1701d.github.io/Clew-Labs/
- Porch Light (current build): mid-build, AWS Agents for Humans

---

*Last updated: September 10, 2026 (v2: added judging criteria, corrected schedule, updated strategy for Observator Clew)*
*AI assisted. Human approved. Powered by NLP.*
