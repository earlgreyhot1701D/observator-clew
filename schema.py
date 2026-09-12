"""
Pydantic models for Observator Clew, per prompts/output_schema.md.

Field-level validation (repo-must-exist-in-snapshot, non-empty what_cant_know,
retry-on-violation) lives in the code that calls the model, not here. These
models define the shape only.
"""

from typing import Literal

from pydantic import BaseModel


class Finding(BaseModel):
    """One per candidate the agent reasoned about."""

    repo: str
    why_surfaced: str
    what_checked: list[str]
    what_found: str
    what_cant_know: str
    recommendation: Literal["SURFACE", "SUPPRESS"]
    recommendation_reason: str
    confidence: Literal["high", "medium", "low"]


class RunResult(BaseModel):
    """The whole run, saved to runs/latest.json."""

    run_at: str
    observed_count: int
    signaled_count: int
    investigated_count: int
    surfaced: list[Finding]
    suppressed: list[Finding]
    auto_suppressed_note: list[str]
