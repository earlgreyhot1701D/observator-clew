# Observator Clew: Pre-Build Prep Plan

**Purpose:** Everything you can (and can't) do before Saturday, September 12. Organized by category with the hackathon rule as the guardrail.

---

## The rule (verbatim from the portal)

> "You can use existing templates, reusable components, libraries, prompts, starter code, and other building blocks, but the project and its core functionality must be built during the event. A pre-existing project cannot be resubmitted or extended and entered as a new hackathon project. Teams must be prepared to explain which parts were created during the hackathon versus what existed before."

## The explain-it test

If a judge asks "what did you build today vs. before?", your answer:

> "I brought my data (GitHub snapshot), my design assets (logo, dashboard template, bot avatar), my prompt templates, and my infrastructure (bot token, API keys, repo skeleton, deploy pipeline). Everything that makes it an agent -- the reasoning logic, the triage pipeline, the Telegram command handlers, the NO_NOTIFICATION decision, the dashboard content generation -- I built today."

That answer must be true. If anything on Saturday's MUST list was already working before you walked in, it's not net-new.

---

## What's allowed before Saturday

### Infrastructure and accounts (do this first)

| Task | Time | Notes |
|---|---|---|
| Create Telegram bot via BotFather | 5 min | Get the token. Set the bot name, description, profile photo. |
| Test sending yourself a Telegram message | 10 min | Verify the token works. Test MarkdownV2 formatting quirks. Learn what breaks. |
| Get OpenAI or OpenRouter API key | 5 min | Have it ready. Don't burn credits testing agent logic (that's core functionality). |
| Get GitHub personal access token | 5 min | For live API stretch goal. Scoped to public repo read. |
| Set up deployment target | 15 min | Cloud Run, Railway, Vercel, or wherever you'll host. Create the project, configure the deploy pipeline. Don't deploy agent code. |
| Create the repo | 5 min | MIT license, .gitignore, README shell, folder structure. No agent code. |
| Install dependencies locally | 10 min | python-telegram-bot, openai, whatever you'll use. Have them in requirements.txt or package.json. This is starter code. |

**Total: ~55 minutes**

### Data (your repos, not agent logic)

| Task | Time | Notes |
|---|---|---|
| Snapshot GitHub repos to JSON | 30 min | Pull metadata for all 60+ repos: name, description, last push, language, archived, topics, homepage, open issues count, default branch. Then for each repo, check for key files (README.md, Dockerfile, vercel.json, package.json, .github/workflows/). Save as `estate-snapshot.json`. |
| Review the snapshot | 15 min | Know your own data. Which repos are interesting? Which are genuinely dormant? What would a good agent notice? This shapes your demo. |

**Total: ~45 minutes**

### Design and artwork (safe as templates/assets)

| Task | Time | Notes |
|---|---|---|
| Observator Clew logo/icon | 30-60 min | For the Telegram bot avatar, the dashboard header, the GitHub repo, and the social post. This is a brand asset, not core functionality. |
| Color palette and typography | 15 min | Pick your colors. Pick your fonts. Have CSS variables ready. This is a design system, same as bringing a UI kit. |
| Dashboard HTML/CSS shell | 45-60 min | A responsive, mobile-friendly (375px) single-column HTML page with your styling, placeholder sections, and no agent-generated content. The agent fills it on Saturday. Be ready to explain: "I prepped the HTML template. The agent generates the content." |
| Telegram bot profile photo | 10 min | Upload it via BotFather. First impression for judges watching the demo video. |
| Social media post graphic | 20 min | Optional. A card or banner for the required social post. Not the post itself (you need the project link first). |

**Total: ~2-3 hours**

### Prompts and templates (explicitly allowed)

| Task | Time | Notes |
|---|---|---|
| System prompt for agent reasoning | 30 min | The instructions that tell the LLM how to evaluate repos, what evidence to cite, when to use uncertainty language, when to return NO_NOTIFICATION. This is a prompt, not code. The code that sends it to the API is Saturday work. |
| Output format templates | 15 min | What the Telegram message structure looks like. What the dashboard JSON schema looks like. These are templates the agent will fill. |
| Demo video script | 20 min | Write the exact narration. Know what Telegram will show. Know what the dashboard will show. Know the closing line. The demo script IS the build spec. |
| Social media post template | 5 min | Draft with blanks for project link and video URL. Tag the event partners. |
| README template | 10 min | Structure for the repo README: what it is, how it works, how to run it, built with, credits. Fill in the project-specific content on Saturday. |

**Total: ~80 minutes**

### Planning and strategy (always allowed)

| Task | Time | Notes |
|---|---|---|
| Review the scoping review doc | 15 min | Know the MUST/STRETCH/STUB/NEVER list cold. |
| Review the ChatGPT build recommendation | 15 min | Once ChatGPT responds to the updated handoff prompt. |
| Build order plan | 15 min | Decide the exact sequence for Saturday. Which file do you open first? What's the first thing you type? |
| Practice the demo flow | 10 min | Walk through the Option C demo beats in your head. Know the story. |

**Total: ~55 minutes**

---

## What's NOT allowed before Saturday

These are all core functionality. They get built during the event.

- **Agent reasoning logic.** The code that sends prompts to the LLM, processes the response, and produces findings. The prompts themselves are fine to write. The code that uses them is Saturday.
- **Telegram command handlers.** The code that listens for /estate or /check and routes to agent logic.
- **GitHub data processing pipeline.** The code that reads the JSON snapshot, triages repos into buckets (active/stale/dormant), and feeds them to the agent.
- **Dashboard content generation.** The code that takes agent findings and writes them into the HTML template. The empty HTML template is fine. The code that fills it is Saturday.
- **NO_NOTIFICATION decision logic.** The code that evaluates whether findings are worth interrupting you. This is the core agent behavior.
- **Integration wiring.** Connecting agent output to Telegram messages to dashboard links. The glue is the agent.
- **Any working end-to-end flow.** If you can trigger the bot and get a real response before Saturday, you've built too much.

---

## Prep schedule

### Today (Wednesday, September 10)

**Priority: Design assets and data snapshot.**

1. Create the Telegram bot, get the token, set the profile photo
2. Snapshot your GitHub repos to JSON
3. Start on artwork: logo, color palette, dashboard template
4. Write prompt templates (system prompt, output format)
5. Script the demo video narration

### Thursday, September 11

**Priority: Templates and environment.**

1. Finish the dashboard HTML/CSS shell (mobile-friendly, test at 375px)
2. Set up the repo skeleton with dependencies listed
3. Set up the deployment target
4. Get all API keys in one place
5. Review ChatGPT's revised build recommendation (if received)
6. Write the build order plan: exact sequence for Saturday

### Friday, September 11

**Priority: Final review and rest.**

1. Review all prep materials: snapshot, templates, prompts, demo script
2. Test that the Telegram bot token still works (send a test message)
3. Make sure your dev environment is ready (IDE, terminal, hot reload)
4. Print or pin the MUST/STRETCH/STUB/NEVER list where you can see it
5. Charge your devices
6. Get sleep

---

## The gray areas (and how to stay safe)

**Dashboard HTML template:** Safe. It's a styled empty page. The agent fills it. Same as bringing a slide template to a presentation hackathon. Just don't put real findings or agent output in it. Use placeholder text like "[Agent findings appear here]" or lorem ipsum.

**Prompt templates:** Explicitly safe. The portal rule says "prompts" are allowed building blocks. Write your system prompt, your output format instructions, your NO_NOTIFICATION criteria. The code that sends them to the API is Saturday.

**Testing MarkdownV2 formatting:** Safe. You're learning the tool, not building the agent. Send test messages with bold, italic, code blocks, links. Note what breaks. Have a cheat sheet ready for Saturday.

**Color palette and CSS:** Safe. Design assets and reusable components. Have your CSS variables file ready to drop into the dashboard and any other output.

**Artwork and logo:** Safe. Brand assets. Not core functionality. Use it for the bot avatar, the dashboard header, the social post, the repo README.

**Pre-computed repo analysis:** NOT safe. If you run analysis on your repos and save the results, that's agent work done before the event. The raw metadata snapshot is fine. Conclusions about that data are Saturday's job.

---

*Prepared: September 10, 2026*
*AI assisted. Human approved. Powered by NLP.*
