"""
Observator Clew, entrypoint.

Block 0: prove the pipe. Send one HTML Telegram message containing bold text,
italic text, and the Estate Overview link from .env. No triage, no agent, no
GitHub calls, no argument parsing. That is later blocks.
"""

import asyncio
import os
import sys

from telegram import Bot
from telegram.constants import ParseMode


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

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
ESTATE_OVERVIEW_URL = os.environ.get("ESTATE_OVERVIEW_URL")


def build_message() -> str:
    """One HTML message: bold, italic, and the clickable Estate Overview link."""
    return (
        "<b>Observator online</b>\n"
        "<i>Creating is becoming nearly free. Maintaining never did.</i>\n\n"
        f'<a href="{ESTATE_OVERVIEW_URL}">View full estate</a>'
    )


async def send_once() -> None:
    bot = Bot(token=BOT_TOKEN)
    await bot.send_message(
        chat_id=CHAT_ID,
        text=build_message(),
        parse_mode=ParseMode.HTML,
    )


def main() -> None:
    if not BOT_TOKEN or not CHAT_ID:
        print("FAIL: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing from .env.")
        sys.exit(1)
    if not ESTATE_OVERVIEW_URL:
        print("FAIL: ESTATE_OVERVIEW_URL missing from .env.")
        sys.exit(1)

    try:
        asyncio.run(send_once())
    except Exception as e:
        # Never surface the token in an error message.
        print(f"FAIL: could not send Telegram message: {type(e).__name__}: {e}")
        sys.exit(1)

    print("Sent. Check Telegram: 'Observator online' with a working Estate Overview link.")


if __name__ == "__main__":
    main()
