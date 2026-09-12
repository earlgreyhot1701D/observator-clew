"""
One-off test: confirms TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, and HTML
parse_mode all work together, before any of this matters for real.

Not part of the agent. Prep-only, per the checklist. Delete or leave it,
doesn't matter either way, it isn't core functionality.

Run: python test_telegram.py
"""

import asyncio
import os

from telegram import Bot


def load_dotenv(path=".env"):
    """Minimal .env loader, no external dependency."""
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

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


async def main():
    if not TOKEN or not CHAT_ID:
        print("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID in .env. Fill those in first.")
        return

    bot = Bot(token=TOKEN)
    await bot.send_message(
        chat_id=CHAT_ID,
        text=(
            "<b>OBSERVATOR CLEW</b>\n\n"
            "<i>If this line is bold and this line is italic, "
            "HTML parse mode works.</i>"
        ),
        parse_mode="HTML",
    )
    print("Sent. Check Telegram, if it's bold/italic you're good.")


if __name__ == "__main__":
    asyncio.run(main())
