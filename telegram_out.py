"""
Build and send the Telegram briefing, per prompts/telegram_template.md.

HTML parse mode. All interpolated text is escaped. The briefing caps at the top
3 surfaced findings; the rest live in the funnel line and the Estate Overview.
Message length is asserted under 4096 before send. callback_data is asserted
under 64 bytes before the keyboard is built, using short index ids, never raw
repo names.
"""

import datetime
import html

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode

TELEGRAM_MAX_CHARS = 4096
CALLBACK_MAX_BYTES = 64
MAX_FINDINGS_IN_BRIEFING = 3


def _esc(text):
    """Escape HTML in interpolated text (repo names and model text alike)."""
    return html.escape(str(text if text is not None else ""))


def run_stamp(run_at):
    """
    Short, stable derivation of run_at for callback_data, so a tap resolves
    against the run it was shown on, not whatever runs/latest.json holds now.
    Digits only from the ISO timestamp (e.g. 2026-09-12T14:15:30.1+00:00 ->
    20260912141530...), truncated to keep callback_data well under 64 bytes.
    """
    return "".join(ch for ch in (run_at or "") if ch.isdigit())[:14]


def id_map_for(run_result):
    """
    Rebuild the idx -> full_name map deterministically from a RunResult, without
    re-rendering HTML. Same order and cap build_briefing uses, so a tap resolved
    here matches what the reader saw.
    """
    surfaced = run_result.surfaced[:MAX_FINDINGS_IN_BRIEFING]
    return {idx: f.repo for idx, f in enumerate(surfaced)}


SEPARATOR = "\u2500" * 10  # box-drawing rule between cards, no emoji

BUTTON_LABEL_MAX = 20
SHORT_NAME_MAX = 12


def _local_timestamp(run_at):
    """
    run_at is stored in UTC. Convert to the system local zone before display,
    never print raw ISO or UTC. Format: "Sep 12, 2:41 PM" (leading zeros on day
    and hour stripped manually, since %-d / %-I are not portable on Windows).
    """
    dt = datetime.datetime.fromisoformat(run_at).astimezone()
    day = str(dt.day)
    hour = str(((dt.hour - 1) % 12) + 1)
    return dt.strftime(f"%b {day}, {hour}:%M %p")


def _suppressed_lines(notes):
    """
    Render the auto-suppressed block from guard.py's note strings, which look
    like "owner/name: No action, 2026-09-12 — evidence unchanged". Show repo
    short name and a "Sep 12" date, matching the locked template section 4.

    A header sentence (correctly pluralized) then one line per repo. If a note
    does not parse, fall back to the raw note so nothing is silently dropped.
    """
    n = len(notes)
    noun = "finding" if n == 1 else "findings"
    lines = [f"<i>{n} previous {noun} suppressed.</i>"]
    for note in notes:
        try:
            full, rest = note.split(": No action, ", 1)
            date_token = rest.split(" ", 1)[0]  # YYYY-MM-DD
            pretty_date = datetime.datetime.strptime(date_token, "%Y-%m-%d").strftime(
                f"%b {int(date_token[8:10])}"
            )
            short = full.split("/")[-1]
            lines.append(
                f"<i>{_esc(short)}: No action, {pretty_date}. "
                "No material evidence has changed.</i>"
            )
        except (ValueError, IndexError):
            lines.append(f"<i>{_esc(note)}</i>")
    return lines


def _finding_block(finding, number):
    """The per-finding HTML block from template 1, numbered to match its buttons."""
    checked = finding.what_checked
    checked_str = ", ".join(checked) if checked else "nothing"
    return (
        f"<b>{number}. {_esc(finding.repo)}</b>\n"
        f"<i>Why this surfaced:</i> {_esc(finding.why_surfaced)}\n"
        f"<i>What I checked:</i> {_esc(checked_str)}\n"
        f"<i>What I found:</i> {_esc(finding.what_found)}\n"
        f"<i>What I can't know:</i> {_esc(finding.what_cant_know)}\n"
        f"<b>Recommendation: {_esc(finding.recommendation)}</b>"
    )


def build_briefing(run_result, estate_overview_url):
    """
    Build the briefing HTML and a run-local id_map (short idx -> full repo name).

    Returns (text, id_map). The id_map lets Block 4 resolve a tapped button back
    to a repo without ever putting the repo name in callback_data.
    """
    surfaced = run_result.surfaced[:MAX_FINDINGS_IN_BRIEFING]
    surfaced_count = len(run_result.surfaced)

    lines = [
        "<b>OBSERVATOR CLEW</b>",
        f"<i>{_esc(_local_timestamp(run_result.run_at))}</i>",
        "",
        (
            f"<b>{run_result.observed_count}</b> observed \u00b7 "
            f"<b>{run_result.signaled_count}</b> signaled \u00b7 "
            f"<b>{run_result.investigated_count}</b> investigated \u00b7 "
            f"<b>{surfaced_count}</b> surfaced"
        ),
        "",
    ]

    # Auto-suppressed block is the headline on a second run ("what changed since
    # you last looked"), so it sits directly under the funnel, above the cards.
    if run_result.auto_suppressed_note:
        lines.extend(_suppressed_lines(run_result.auto_suppressed_note))
        lines.append("")
        lines.append(SEPARATOR)
        lines.append("")

    id_map = {}
    for idx, finding in enumerate(surfaced):
        id_map[idx] = finding.repo
        lines.append(_finding_block(finding, idx + 1))
        lines.append("")
        # Separator between cards only, never after the last.
        if idx < len(surfaced) - 1:
            lines.append(SEPARATOR)
            lines.append("")

    # Reconcile the header count with the visible cards. The funnel is the
    # honesty check; it cannot be the number that does not add up.
    if surfaced_count > len(surfaced):
        lines.append(
            f"<i>Showing the top {len(surfaced)} of {surfaced_count} surfaced. "
            "The rest are on the Estate Overview.</i>"
        )
        lines.append("")

    lines.append(f'<a href="{_esc(estate_overview_url)}">View full estate</a>')

    return "\n".join(lines), id_map


def _button_label(number, action_word, repo):
    """"{n} {action} {short}" if the short name fits, else "{n} {action}".

    Number matches the card header so a tapped pair is unambiguous. Label kept
    under 20 chars so rows do not wrap on mobile.
    """
    short = repo.split("/")[-1]
    if len(short) <= SHORT_NAME_MAX:
        with_name = f"{number} {action_word} {short}"
        if len(with_name) < BUTTON_LABEL_MAX:
            return with_name
    return f"{number} {action_word}"


def build_keyboard(id_map, stamp):
    """
    Two buttons per surfaced finding, numbered to match their card. callback_data
    is "{action}:{stamp}:{idx}", asserted under 64 bytes. The stamp ties the tap
    to the run it was shown on; the idx indexes id_map. Never the raw repo name.
    """
    rows = []
    for number, idx in enumerate(sorted(id_map), start=1):
        repo = id_map[idx]
        investigate_cb = f"investigate:{stamp}:{idx}"
        noaction_cb = f"noaction:{stamp}:{idx}"
        for cb in (investigate_cb, noaction_cb):
            assert len(cb.encode("utf-8")) < CALLBACK_MAX_BYTES, (
                f"callback_data too long: {cb!r}"
            )
        rows.append(
            [
                InlineKeyboardButton(
                    _button_label(number, "Investigate", repo),
                    callback_data=investigate_cb,
                ),
                InlineKeyboardButton(
                    _button_label(number, "No action", repo),
                    callback_data=noaction_cb,
                ),
            ]
        )
    return InlineKeyboardMarkup(rows) if rows else None


async def send_briefing(bot, chat_id, run_result, estate_overview_url):
    """
    Build and send one briefing. Asserts length < 4096 before sending.
    Returns the id_map. try/except on the network call; token never surfaced.
    """
    text, id_map = build_briefing(run_result, estate_overview_url)
    assert len(text) < TELEGRAM_MAX_CHARS, (
        f"briefing is {len(text)} chars, over the {TELEGRAM_MAX_CHARS} limit"
    )
    keyboard = build_keyboard(id_map, run_stamp(run_result.run_at))
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )
    except Exception as e:
        print(f"FAIL: could not send briefing: {type(e).__name__}: {e}")
        raise
    return id_map
