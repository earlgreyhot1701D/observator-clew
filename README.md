# Observator Clew

Creating is becoming nearly free. Maintaining never did.

Most agents are designed to say more. Observator is designed to learn when not to bother you.

Observator watches one person's GitHub estate and decides what actually needs their attention. It doesn't summarize everything. It surfaces what matters, explains why in plain language, and remembers what you've already told it not to bring up again.

Built solo by La Shara Cordero at the AI Tinkerers "Agents, Everywhere" hackathon, Sep 12, 2026.

## How it works

A deterministic layer scans the estate and flags candidates worth a closer look. An agent investigates only those candidates, requesting evidence it actually needs, and recommends SURFACE or SUPPRESS with a reason either way. A persistence guard checks prior decisions before the agent is ever called again, so a repo you've already said "no action" on stays quiet unless something material changes.

Every finding, surfaced or suppressed, comes with four things: why it surfaced, what was checked, what was found, and what can't be known from the data alone. Unknown is a legitimate answer here, not a failure.

## Prepared before the event

Per the hackathon rules, existing templates, prompts, and starter tooling are allowed before build day; core functionality is not. Here's what's pre-existing and what's new tomorrow.

- `estate-snapshot.json` — a GitHub estate snapshot, collected Sep 10. Structural data only, not analyzed or used to pre-select findings.
- `snapshot_estate.py` — the data collection script that produced it.
- `branding/` — visual identity assets.
- `docs/index.html` — an empty page shell with placeholder content only, no real data or logic.
- `planning/` — scoping, review, and architecture documents.
- `prompts/` — the system prompt, output schema spec, and Telegram message templates the agent will use. Prompts are allowed as prep; the code that invokes them is not.

## Built during the event

(filled in on Sep 12 — this section will list what was actually built at the hackathon, so anyone can see exactly what's new versus what existed going in.)
