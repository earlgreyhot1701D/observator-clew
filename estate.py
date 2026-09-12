"""
Loads estate-snapshot.json. Nothing else.

The snapshot is inherited prep data (collected before the event, declared in
the README). This module reads it; it does not interpret or filter it.
"""

import json


def load_snapshot(path="estate-snapshot.json"):
    """Return the parsed snapshot dict: owner, captured_at, repo_count, repos."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)
