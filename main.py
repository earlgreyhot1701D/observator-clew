"""
Observator Clew does not run as a one-shot script.

It is a long-running process that pushes an unprompted briefing at
startup and then stays up, so inline buttons from earlier runs stay
live. Start it with:

    python bot.py

This file was the Block 0 smoke test that proved the Telegram pipe
before any of the pipeline existed. It is kept as a signpost, not an
entry point.
"""

print("Observator Clew runs as a process. Start it with: python bot.py")
