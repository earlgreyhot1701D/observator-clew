# Observator Clew, Telegram Message Templates (v1, prepared before event)

All messages use `parse_mode="HTML"`. Escape `<`, `>`, `&` in any
interpolated text (repo names and model-generated text both, a repo
description or a model sentence could contain any of these).

Hard limit: 4096 characters per message. Cap the briefing at the top 3
findings by SURFACE order; anything beyond that is summarized in the
funnel line and left to the Estate Overview page.

---

## 1. The briefing (unprompted push)

```
<b>OBSERVATOR CLEW</b>

<b>{observed}</b> observed · <b>{signaled}</b> signaled · <b>{investigated}</b> investigated · <b>{surfaced_count}</b> surfaced

{for each surfaced finding, up to 3:}
<b>{repo}</b>
<i>Why this surfaced:</i> {why_surfaced}
<i>What I checked:</i> {what_checked joined with ", " or "nothing" if empty}
<i>What I found:</i> {what_found}
<i>What I can't know:</i> {what_cant_know}
<b>Recommendation: {recommendation}</b>

[ Investigate ]  [ No action ]
{blank line between findings}

{if auto_suppressed_note is non-empty:}
<i>{count} previous finding(s) suppressed, no material change since your last decision.</i>

<a href="{estate_overview_url}">View full estate</a>
```

Inline keyboard: two buttons per finding. `callback_data` has a hard 64-byte
limit and **the repo name is not safe to put in raw**. With an owner prefix of
`earlgreyhot1701D/` eating 17 bytes, a long repo name can push the string past
the limit, and the button then fails for whichever repo triage happened to pick,
not one you get to choose in advance.

Encode short, fixed-width identifiers for both parts:
`{action}:{repo_idx_or_short_hash}:{fingerprint_short_hash}`
Keep a run-local map from the short id back to the full repo name. Assert the
encoded string is under 64 bytes before building the keyboard, the same way
message length is asserted before sending.

**Call `await query.answer()` as the first line of the callback handler.**
This is separate from editing or replying to the message. Without it,
`python-telegram-bot` leaves the tapped button showing a spinning clock in the
client, so a tap that succeeded on the backend looks broken on camera while you
narrate "decision recorded." Answer first, then do the work.

## 2. Button acknowledgment (edit the message or reply, either works, decide Saturday based on what's faster to wire)

Investigate pressed:
```
Noted. I'll keep this one visible until you tell me otherwise.
```

No action pressed:
```
Decision recorded. I won't surface this again unless the evidence
materially changes.
```

## 3. Quiet run (nothing to surface at all)

```
<b>OBSERVATOR CLEW</b>

I checked your estate. {observed} observed, {signaled} signaled,
{investigated} investigated. Nothing needs you right now.
```

(This is the fixture/test-estate case from the build-day review, kept in
the repo and README, not necessarily shown in the demo video.)

## 4. Second-run suppression line (the demo's closing beat, this is just
the briefing template above, but written out once so the exact wording is
locked and doesn't get improvised live)

```
<b>OBSERVATOR CLEW</b>

<b>{observed}</b> observed · <b>{signaled}</b> signaled · <b>{investigated}</b> investigated · <b>{surfaced_count}</b> surfaced

{remaining real findings, if any, using template 1's per-finding block}

<i>1 previous finding suppressed, {repo}: No action, {date}.
No material evidence has changed.</i>

<a href="{estate_overview_url}">View full estate</a>
```

---

## Formatting notes

- No MarkdownV2 anywhere. HTML only, per the build-day review.
- Bold (`<b>`) for repo names, labels, and the recommendation line. Italic
  (`<i>`) for the four grammar fields and the suppression note. Nothing
  else styled, the Bauhaus restraint applies to Telegram too.
- The funnel line format (`60 observed · 7 signaled · 3 investigated · 2
  surfaced`) is fixed. Don't reorder or rename the four words; they're the
  same four words used on the Estate Overview page and in the README.
