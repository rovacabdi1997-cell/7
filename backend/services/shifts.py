"""Shift schedule from config. A shift may cross midnight (end <= start)."""
from datetime import datetime

from app.timeutil import hhmm_to_minutes


def _span(shift: dict) -> tuple[int, int]:
    start = hhmm_to_minutes(shift["start"])
    end = hhmm_to_minutes(shift["end"])
    if end <= start:
        end += 24 * 60
    return start, end


def _in_window(minute: int, start: int, end: int) -> bool:
    return start <= minute < end or start <= minute + 24 * 60 < end


def shift_state(shifts: list[dict], now: datetime) -> dict:
    minute = now.hour * 60 + now.minute
    for index, shift in enumerate(shifts):
        start, end = _span(shift)
        if not _in_window(minute, start, end):
            continue
        elapsed = (minute - start) % (24 * 60)
        b_start, b_end = hhmm_to_minutes(shift["breakStart"]), hhmm_to_minutes(shift["breakEnd"])
        return {
            "current": shift,
            "next": shifts[(index + 1) % len(shifts)],
            "elapsedMin": elapsed,
            "remainingMin": (end - start) - elapsed,
            "onBreak": b_start <= minute < b_end,
        }
    raise ValueError(f"No shift covers {now:%H:%M}; check plant.json")
