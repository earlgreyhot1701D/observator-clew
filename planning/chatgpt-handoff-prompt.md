# Prompt for ChatGPT: Updated Observator Clew Hackathon Scoping

I had your Observator Clew hackathon analysis reviewed against the actual PRD, the hackathon handbook, and my build history. Here's what came back. Fold this into your build recommendation.

## Schedule correction

Submissions are due at 3:30 PM, not 5:00 PM. The show-and-tell happens AFTER submissions close (4:00-4:45 PM). That means the real build window is 11:15 AM to ~3:15 PM if I want any buffer. Call it 4 hours flat.

## Judging criteria are now published

Four criteria, each scored 1-5 by global judges. These are the actual rubrics from the portal:

**1. Core Requirements & Functionality:** Does the project deliver a working agent inside a place where people already work, talk, or live? Does the core workflow function end to end? A 1 means it doesn't run. A 5 means robust, reliable, fully functional.

**2. Innovation & Theme Alignment:** Does the project explore a compelling new place or interaction for agents? Does the environment materially improve what the agent can do? A 2 is "the environment mostly serves as a wrapper." A 5 is "reveals a surprising new agent pattern whose central value could not be reproduced in a standalone chatbox."

**3. Technical Execution & Integration:** Code, architecture, reliability, tool use, data handling, depth of integration. A 5 is "exceptional engineering, robust orchestration, thoughtful failure handling, deeply integrated architecture."

**4. Usefulness & Agentic Experience:** Clear value for intended users? Agent intuitive, effective, appropriate? A 5 is "unlocks substantial value through agent experience designed specifically for its environment, uses context intelligently while remaining clear and controllable."

These rubrics should shape every build decision. Specifically: Telegram cannot be a wrapper (that's a 2 on Innovation). The "should I interrupt you?" decision logic is what makes the environment essential, not decorative.

## Feasibility concerns from the review

Your analysis underestimates integration time in three places:

1. **GitHub API across 60+ repos:** Multiple endpoints per repo (repos, contents, workflows, languages, issues). Rate limiting at 5,000 requests/hour. Pagination. Parsing file contents (README, Dockerfile, vercel.json) requires individual API calls. This is 60-90 minutes if wired live. Mitigation: pre-snapshot repos into JSON before Saturday.

2. **Telegram bot wiring:** Creating the bot token via BotFather takes 2 minutes. Wiring webhook/polling, MarkdownV2 formatting (famously picky), command handlers, inline keyboard buttons, and error handling is 45-60 minutes of real work.

3. **Trigger.dev is TypeScript-native.** If the agent is Python (my stronger language for agent work), there's a language mismatch. Wiring Trigger.dev means learning their SDK, project structure, and deployment model in a 4-hour window. Alternative: manual trigger for the demo, stub comment for Trigger.dev.

## Three Telegram commands is two too many

/estate, /check, /brief in 4 hours with GitHub API + Telegram + agent reasoning + dashboard is ambitious. /estate is MUST. /check is the priority stretch goal (lifts Innovation + Usefulness scores). /brief is a stub.

## The dashboard must be mobile-friendly

The Telegram link opens in a phone browser. If the dashboard breaks on mobile, the demo breaks at the exact moment it's supposed to land. Single-column, responsive, readable at 375px. Not optional polish. The dashboard link IS the action channel: notification to detail in one tap.

## Demo format decision: Option C (confirmed)

I'm going with **notification + /check follow-up** for the 2-minute demo:

1. **Beat 1:** Agent sends unprompted Telegram notification. It says: "I reviewed 47 repos. 3 need your attention. Here's the evidence." The 44-repo silence is quantified, not hidden. This proves the agent comes to you AND exercises judgment about what's worth your time.
2. **Beat 2:** I reply `/check observator-clew` and the agent responds with repo-specific detail. This proves Telegram is a conversation, not a one-way pipe.
3. **Beat 3:** Tap the dashboard link. Opens on phone, mobile-friendly, full estate at a glance.

## The decision-making is the feature, not plumbing

The agent's triage reasoning must be VISIBLE in every notification. Not just "repo X has a problem" but "I reviewed your estate. 3 of 47 repos need attention. Here's what I found and why." The 44 repos the agent chose NOT to surface are part of the story. This is what lifts Usefulness from "basic prompt and response" (score 2) to "context-intelligent, clear, controllable" (score 4-5).

## Multi-channel: stub the email, build the dashboard link

The notification should include a line like "📧 Detailed report sent to your email" as a text stub signaling multi-channel design. The email body could be generated as a text file alongside the dashboard HTML (same output, different format, 15 minutes if time allows). Don't wire SMTP. The dashboard link is the real action channel and it's already being built.

## What I want from you now

Revise your build recommendation with these constraints factored in:
- 4 hours flat (not 4.25)
- Build to the four judging criteria, especially Innovation (environment must be essential, not a wrapper) and Usefulness (context-intelligent, clear, controllable)
- Account for the realistic integration times above
- Demo format is Option C: notification + /check + dashboard link
- Visible triage reasoning in notifications is a MUST, not a nice-to-have
- /check is the priority stretch goal; /brief is a stub
- Email action channel is a stub (text line in notification + optional generated email body file)
- The dashboard is a single static HTML page generated by the agent, mobile-friendly, no frontend framework
- Language decision needed: Python throughout, or TypeScript for Trigger.dev alignment?
