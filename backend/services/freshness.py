"""Age check applied to every snapshot before it leaves the API.

A HAKYKY value whose sourceTs is older than its staleAfterSec becomes KONE; a
HAKYKY value without sourceTs cannot prove its age and becomes KONE too. The
value itself is kept: the screen shows it faded and marked, never as running.
Line and snapshot modes are then summarised from their fields."""
from datetime import datetime
from typing import Iterable

from pydantic import BaseModel

from app.models import DataMode, Snapshot


def _walk(obj) -> Iterable[BaseModel]:
    if isinstance(obj, BaseModel):
        yield obj
        for name in type(obj).model_fields:
            yield from _walk(getattr(obj, name))
    elif isinstance(obj, list):
        for item in obj:
            yield from _walk(item)


def summary(modes: Iterable[DataMode]) -> DataMode:
    """KONE wins (something is old), then HAKYKY, then SIMULYASIYA; nothing = MAGLUMAT_YOK."""
    seen = set(modes)
    for mode in ("KONE", "HAKYKY", "SIMULYASIYA"):
        if mode in seen:
            return mode
    return "MAGLUMAT_YOK"


def mark_stale(snap: Snapshot, now: datetime) -> Snapshot:
    for item in _walk(snap):
        if getattr(item, "mode", None) != "HAKYKY" or not hasattr(item, "staleAfterSec"):
            continue
        ts = item.sourceTs
        if ts is None or (now - ts).total_seconds() > item.staleAfterSec:
            item.mode = "KONE"
    for line in snap.lines:
        # CONFIG fields (nominal capacity) are reference figures and do not decide the line's mode.
        line.mode = summary(m.mode for m in _walk(line)
                            if m is not line and hasattr(m, "staleAfterSec") and getattr(m, "sourceType", "") != "CONFIG")
    snap.dataMode = summary(line.mode for line in snap.lines)
    return snap
