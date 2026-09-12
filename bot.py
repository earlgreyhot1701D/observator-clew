"""
One long-running Telegram Application. Pushes the briefing at startup via
job_queue, and a bare /run command re-triggers a run inside the same process
(no restart, so inline buttons from earlier runs stay live).

Also: every run writes runs/latest.json, and --replay reads it and resends the
briefing without any model or GitHub call.

The run pipeline:
  snapshot -> triage -> select signaled candidates -> cap oldest N -> reason
  -> assemble RunResult -> write runs/latest.json -> send briefing.

signaled = (quiet OR long-quiet) AND has_deployment_evidence. That is the
thesis: quiet things that were deployed may still need attention.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

from dashboard import render_dashboard
from estate import load_snapshot
from guard import clear_decisions, persistence_guard, policy_guard, record_decision
from reason import reason
from schema import Finding, RunResult
from telegram_out import id_map_for, run_stamp, send_briefing
from triage import _age_days, _parse_dt, triage

RUNS_PATH = "runs/latest.json"

# One logger for this file, to stdout, INFO. No file, no rotation, no config.
# Never logs the token or any env value.
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", stream=sys.stdout)
log = logging.getLogger("observator.bot")


def load_dotenv(path=".env"):
    """Minimal .env loader, same pattern as the repo's other scripts."""
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


load_dotenv()

# Read after load_dotenv so a value in .env is honored; a real shell env var
# still wins because load_dotenv uses setdefault. Lowering it speeds up a run.
MAX_CANDIDATES = int(os.environ.get("MAX_CANDIDATES", "5"))

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
ESTATE_OVERVIEW_URL = os.environ.get("ESTATE_OVERVIEW_URL")


def _signaled(records):
    """(quiet OR long-quiet) AND has_deployment_evidence."""
    return [
        r
        for r in records
        if r["bucket"] in ("quiet", "long-quiet") and r["has_deployment_evidence"]
    ]


def _select_candidates(records, snapshot):
    """
    Return (signaled_records, candidates). Candidates are the MAX_CANDIDATES
    oldest-by-days-quiet from the signaled set: longest-quiet is likeliest to be
    forgotten, and 5 to fill 3 briefing slots is proportionate.
    """
    captured_at = _parse_dt(snapshot.get("captured_at"))
    by_full = {r.get("full_name"): r for r in snapshot.get("repos", [])}

    signaled = _signaled(records)

    def days_quiet(rec):
        age = _age_days(by_full.get(rec["full_name"], {}), captured_at)
        return age if age is not None else -1

    ranked = sorted(signaled, key=days_quiet, reverse=True)
    return signaled, ranked[:MAX_CANDIDATES]


def build_run_result(snapshot):
    """
    Run the full pipeline and return a RunResult. investigated_count is the
    number actually sent to the model (the cap); the funnel discloses the gap
    between signaled and investigated.
    """
    records = triage(snapshot)
    signaled, candidates = _select_candidates(records, snapshot)

    # Persistence guard runs BEFORE the model. Auto-suppressed candidates are
    # never sent to reason(), so investigated_count drops when one is skipped.
    to_investigate, auto_suppressed_notes = persistence_guard(candidates, snapshot)

    findings, dropped = reason(to_investigate, snapshot)

    # Policy guard: the model recommends; this decides what actually interrupts.
    surfaced = policy_guard(findings)
    suppressed = [f for f in findings if f.recommendation == "SUPPRESS"]

    return RunResult(
        run_at=datetime.now(timezone.utc).isoformat(),
        observed_count=snapshot.get("repo_count", len(snapshot.get("repos", []))),
        signaled_count=len(signaled),
        investigated_count=len(to_investigate),
        surfaced=surfaced,
        suppressed=suppressed,
        auto_suppressed_note=auto_suppressed_notes,
    )


def write_latest(run_result):
    """Persist the run so --replay can resend it without any model/GitHub call."""
    os.makedirs(os.path.dirname(RUNS_PATH), exist_ok=True)
    with open(RUNS_PATH, "w", encoding="utf-8") as f:
        json.dump(run_result.model_dump(), f, indent=2)


def read_latest():
    """Load runs/latest.json back into a RunResult."""
    with open(RUNS_PATH, encoding="utf-8") as f:
        return RunResult(**json.load(f))


async def _keep_typing(bot):
    """
    Re-send the 'typing' chat action every 4s so it does not lapse during a
    slow run (Telegram clears it after ~5s). A cosmetic indicator failing must
    never kill the run, so a send error is logged and the loop continues.
    """
    while True:
        try:
            await bot.send_chat_action(chat_id=CHAT_ID, action=ChatAction.TYPING)
        except Exception as e:
            log.info("keep_typing: send_chat_action failed: %s: %s", type(e).__name__, e)
        await asyncio.sleep(4)


async def run_observation(bot):
    """One full run: immediate ack -> pipeline -> write latest.json -> briefing.

    The 'Observing...' message and a repeating typing indicator go out before any
    work starts, so /run is not dead air on camera. The ack message is never
    edited or deleted; a visible start and a visible finish both stay in the chat.
    """
    log.info("run_observation: start")

    # Load the snapshot first (a cheap local file read) so the ack can name the
    # real repository count and set the time expectation. Reused below.
    snapshot = load_snapshot()
    n_repos = snapshot.get("repo_count", len(snapshot.get("repos", [])))

    # Acknowledge immediately, before any model/GitHub work, so the screen is
    # not dead during a 30-60s run.
    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=(
                "<b>OBSERVATOR CLEW</b>\n"
                f"<i>Observing {n_repos} repositories. This usually takes under a minute.</i>"
            ),
            parse_mode="HTML",
        )
    except Exception as e:
        log.info("run_observation: ack send failed: %s: %s", type(e).__name__, e)

    typing_task = asyncio.create_task(_keep_typing(bot))
    try:
        run_result = build_run_result(snapshot)
        write_latest(run_result)
        # Render BEFORE the briefing so the Estate Overview link resolves to this
        # run's data the instant it is tapped. A broken page is bad; a lost
        # briefing is worse, so a render failure logs and the briefing still sends.
        try:
            render_dashboard(run_result)
        except Exception as e:
            log.info("run_observation: dashboard render failed: %s: %s", type(e).__name__, e)
        await send_briefing(bot, CHAT_ID, run_result, ESTATE_OVERVIEW_URL)
        log.info(
            "run_observation: done observed=%d signaled=%d investigated=%d surfaced=%d",
            run_result.observed_count,
            run_result.signaled_count,
            run_result.investigated_count,
            len(run_result.surfaced),
        )
    finally:
        typing_task.cancel()
        try:
            await typing_task
        except asyncio.CancelledError:
            pass


# ---- Handlers ----

async def _startup_push(context: ContextTypes.DEFAULT_TYPE):
    """job_queue callback: the unprompted push at startup."""
    await run_observation(context.bot)


async def run_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bare /run: re-trigger a run inside the same running Application."""
    await run_observation(context.bot)


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Demo tooling: clear the decision store between recording takes.

    Empties state/decisions.json only; does not touch runs/latest.json, the
    snapshot, or anything else.
    """
    count = clear_decisions()
    log.info("reset: cleared %d decisions", count)
    await update.message.reply_text(f"Cleared {count} decision(s).")


# Verbatim template section 2 wording. An identifying line is prefixed above it,
# but the sentence itself is not rewritten.
ACK_INVESTIGATE = "Noted. I'll keep this one visible until you tell me otherwise."
ACK_NO_ACTION = (
    "Decision recorded. I won't surface this again unless the evidence "
    "materially changes."
)
STALE_MESSAGE = "That briefing is from an earlier run. Use the most recent one."


async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Inline button handler for both Investigate and No action.

    query.answer() is the FIRST line and fires exactly once: it stops the
    spinner. A callback query can only be answered once, so every refusal path
    sends its message as a REPLY, never a second answer(). The reply also
    persists on screen, which is better on camera than a toast.
    """
    query = update.callback_query
    await query.answer()
    log.info("on_button: entry data=%r", query.data)

    # callback_data is "{action}:{stamp}:{idx}". Old briefings carry a two-part
    # form ("noaction:0") that fails this unpack -- refuse with feedback, never
    # a silent return.
    try:
        action, stamp, idx_str = query.data.split(":", 2)
        idx = int(idx_str)
    except (ValueError, AttributeError):
        log.info("on_button: exit=parse_failure data=%r", query.data)
        await query.message.reply_text(STALE_MESSAGE)
        return

    # If latest.json is missing or malformed, refuse cleanly and record nothing.
    try:
        run_result = read_latest()
    except (OSError, ValueError) as e:
        log.info("on_button: exit=latest_read_failure err=%s: %s", type(e).__name__, e)
        await query.message.reply_text(STALE_MESSAGE)
        return

    # Run identity check: a tap on an older briefing after a newer run wrote
    # latest.json must not resolve idx against the wrong run. Record nothing.
    current = run_stamp(run_result.run_at)
    if stamp != current:
        log.info("on_button: exit=stale_stamp tapped=%s current=%s", stamp, current)
        await query.message.reply_text(STALE_MESSAGE)
        return

    id_map = id_map_for(run_result)
    repo = id_map.get(idx)
    if repo is None:
        log.info("on_button: exit=idx_not_in_map idx=%s keys=%s", idx, sorted(id_map))
        await query.message.reply_text(STALE_MESSAGE)
        return

    snapshot = load_snapshot()
    by_full = {r.get("full_name"): r for r in snapshot.get("repos", [])}
    repo_record = by_full.get(repo, {})

    decision = "investigate" if action == "investigate" else "no_action"
    record_decision(repo, decision, repo_record)
    log.info("on_button: exit=success repo=%s decision=%s", repo, decision)

    short = repo.split("/")[-1]
    sentence = ACK_INVESTIGATE if decision == "investigate" else ACK_NO_ACTION
    await query.message.reply_text(
        f"<b>{short}</b>\n{sentence}",
        parse_mode="HTML",
    )


def build_application():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("run", run_command))
    app.add_handler(CommandHandler("reset", reset_command))
    app.add_handler(CallbackQueryHandler(on_button))
    app.job_queue.run_once(_startup_push, when=0)
    return app


# ---- Entrypoints ----

async def _replay():
    """Resend the last run's briefing. No model, no GitHub, no triage."""
    from telegram import Bot

    run_result = read_latest()
    bot = Bot(token=BOT_TOKEN)
    await send_briefing(bot, CHAT_ID, run_result, ESTATE_OVERVIEW_URL)
    print("Replayed runs/latest.json to Telegram.")


def main():
    if not BOT_TOKEN or not CHAT_ID:
        print("FAIL: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing from .env.")
        sys.exit(1)
    if not ESTATE_OVERVIEW_URL:
        print("FAIL: ESTATE_OVERVIEW_URL missing from .env.")
        sys.exit(1)

    if "--replay" in sys.argv:
        asyncio.run(_replay())
        return

    app = build_application()
    print("Observator running. Startup briefing queued; /run re-triggers. Ctrl-C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()
