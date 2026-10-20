"""Writes demo snapshots for the offline USB build.

- day.json: one production day, every 3 minutes. The frontend picks the
  snapshot that matches the current Asgabat clock, so the offline screens show
  the same numbers the API would.
- sunum.json: the 6-minute presentation loop (DEMO_SCENARIO=presentation),
  every 5 seconds. The two TV screens play it so a fault and its recovery are
  always shown, exactly as the API's presentation mode would.
"""
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from adapters.demo import PRESENTATION_CYCLE_S, DemoAdapter  # noqa: E402
from app.timeutil import TM_TZ  # noqa: E402

STEP_MIN = 3
SUNUM_STEP_S = 5


def _write(out: Path, payload: dict) -> None:
    out.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{len(payload['snapshots'])} snapshots, {out.stat().st_size / 1e6:.1f} MB -> {out}")


def main() -> None:
    out_dir = ROOT / "frontend" / "public" / "replay"
    out_dir.mkdir(parents=True, exist_ok=True)

    start = datetime(2026, 10, 18, 8, 0, tzinfo=TM_TZ)
    clock_time = start
    adapter = DemoAdapter(lambda: clock_time)
    snapshots = []
    for step in range(24 * 60 // STEP_MIN):
        clock_time = start + timedelta(minutes=step * STEP_MIN)
        snapshots.append(adapter.snapshot().model_dump(mode="json"))
    _write(out_dir / "day.json", {"stepMinutes": STEP_MIN, "dayStartHour": 8, "snapshots": snapshots})

    # The loop position comes from (minute * 60 + second) % cycle, so a base at a
    # full hour makes snapshot i the loop second i * step.
    loop_start = datetime(2026, 10, 18, 14, 0, tzinfo=TM_TZ)
    clock_time = loop_start
    adapter = DemoAdapter(lambda: clock_time, scenario="presentation")
    snapshots = []
    for step in range(PRESENTATION_CYCLE_S // SUNUM_STEP_S):
        clock_time = loop_start + timedelta(seconds=step * SUNUM_STEP_S)
        snapshots.append(adapter.snapshot().model_dump(mode="json"))
    _write(out_dir / "sunum.json", {"stepSeconds": SUNUM_STEP_S, "cycleSeconds": PRESENTATION_CYCLE_S, "snapshots": snapshots})


if __name__ == "__main__":
    main()
