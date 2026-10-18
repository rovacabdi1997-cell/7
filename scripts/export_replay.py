"""Writes one production day of demo snapshots (every 3 minutes) for the
offline USB build. The frontend picks the snapshot that matches the current
Asgabat clock, so the offline screens show the same numbers the API would."""
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from adapters.demo import DemoAdapter  # noqa: E402
from app.timeutil import TM_TZ  # noqa: E402

STEP_MIN = 3


def main() -> None:
    out = ROOT / "frontend" / "public" / "replay" / "day.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    start = datetime(2026, 10, 18, 8, 0, tzinfo=TM_TZ)
    snapshots = []
    clock_time = start
    adapter = DemoAdapter(lambda: clock_time)
    for step in range(24 * 60 // STEP_MIN):
        clock_time = start + timedelta(minutes=step * STEP_MIN)
        snapshots.append(adapter.snapshot().model_dump(mode="json"))
    payload = {"stepMinutes": STEP_MIN, "dayStartHour": 8, "snapshots": snapshots}
    out.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{len(snapshots)} snapshots, {out.stat().st_size / 1e6:.1f} MB -> {out}")


if __name__ == "__main__":
    main()
