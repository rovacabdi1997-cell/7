"""Contract v2 (TAM-PLAN-v9 §7, §24, K13–K15)."""
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel

from adapters.demo import DemoAdapter
from adapters.wincc_sql import WinCCSqlAdapter
from app.config import API_VERSION
from app.contract import FIELDS
from app.main import create_app
from app.models import FieldMeta, Metric, Snapshot
from app.timeutil import TM_TZ
from services.kpi import oee

ROOT = Path(__file__).resolve().parent.parent
API_DIR = ROOT / "docs" / "api"


def walk(obj):
    if isinstance(obj, BaseModel):
        yield obj
        for name in type(obj).model_fields:
            yield from walk(getattr(obj, name))
    elif isinstance(obj, list):
        for item in obj:
            yield from walk(item)


def demo_snapshots(fixed_clock):
    for hour, minute in ((9, 0), (13, 7), (15, 25), (2, 30)):
        yield DemoAdapter(fixed_clock(hour, minute)).snapshot()
    yield DemoAdapter(fixed_clock(10, 2), scenario="presentation").snapshot()


class Source:
    def __init__(self, rows):
        self.rows, self.fail = rows, False

    def query(self, sql):
        if self.fail:
            raise ConnectionError("down")
        return self.rows


def verified(key, **extra):
    return {"key": key, "status": "VERIFIED", "query": "SELECT v FROM t", **extra}


class Clock:
    def __init__(self, start):
        self.now = start

    def __call__(self):
        return self.now


# --- K13: contract files exist, match the code and carry one version ---

def test_contract_files_are_up_to_date():
    result = subprocess.run([sys.executable, str(ROOT / "scripts" / "export_contract.py"), "--check"],
                            capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 0, result.stdout + result.stderr


def test_versions_match():
    spec = json.loads((API_DIR / "openapi.json").read_text(encoding="utf-8"))
    header = (API_DIR / "API-SOZLESMESI.md").read_text(encoding="utf-8").splitlines()[0]
    assert spec["info"]["version"] == API_VERSION
    assert header == f"# API sözleşmesi — sürüm {API_VERSION}"


@pytest.mark.parametrize("path", sorted((API_DIR / "examples").glob("*.json")), ids=lambda p: p.name)
def test_examples_validate_against_schema(path):
    snap = Snapshot.model_validate(json.loads(path.read_text(encoding="utf-8")))
    assert snap.contractVersion == API_VERSION


# --- K14: every field carries unit, source, mode and age limit ---

def test_every_field_has_the_six_facts(fixed_clock):
    for snap in demo_snapshots(fixed_clock):
        fields = [x for x in walk(snap) if isinstance(x, FieldMeta)]
        assert fields
        for f in fields:
            assert f.source and f.sourceType and f.staleAfterSec > 0
            assert f.mode == "MAGLUMAT_YOK" or f.sourceTs is not None
            if isinstance(f, Metric):
                assert f.unit


def test_every_line_value_is_in_the_contract_table(fixed_clock):
    line = DemoAdapter(fixed_clock(13)).snapshot().lines[0]
    for name in type(line).model_fields:
        value = getattr(line, name)
        if isinstance(value, FieldMeta):
            assert f"line.{name}" in FIELDS, name
    for name in type(line.oee).model_fields:
        assert f"line.oee.{name}" in FIELDS


def test_timestamps_are_utc(fixed_clock):
    body = DemoAdapter(fixed_clock(13)).snapshot().model_dump()
    assert body["timestamp"] == "2026-10-18T08:00:00Z"
    assert body["productionDayStart"] == "2026-10-18T03:00:00Z"
    assert body["lines"][0]["speed"]["sourceTs"].endswith("Z")


def test_missing_values_are_null_never_zero(fixed_clock):
    snap = WinCCSqlAdapter(None, fixed_clock(13), {"fields": []}).snapshot()
    assert snap.dataMode == "MAGLUMAT_YOK" and snap.connection.state == "NOT_CONFIGURED"
    for f in walk(snap):
        if isinstance(f, Metric) and f.sourceType != "CONFIG":
            assert f.value is None and f.mode == "MAGLUMAT_YOK"
    demo = DemoAdapter(fixed_clock(13)).snapshot()
    assert demo.energy.powerKw.value is None and demo.energy.powerKw.mode == "MAGLUMAT_YOK"


# --- K15: KONE ---

def test_real_value_turns_kone_after_its_age_limit():
    clock = Clock(datetime(2026, 10, 18, 13, tzinfo=TM_TZ))
    source = Source([{"v": 31.4}])
    adapter = WinCCSqlAdapter(source, clock, {"fields": [verified("gipsokarton.speed")]})
    first = adapter.snapshot()
    assert first.lines[0].speed.mode == "HAKYKY" and first.connection.state == "ONLINE"

    source.fail = True
    clock.now += timedelta(seconds=10)
    within = adapter.snapshot()
    assert within.lines[0].speed.mode == "HAKYKY" and within.lines[0].speed.value == 31.4
    assert within.connection.state == "OFFLINE"

    clock.now += timedelta(seconds=10)
    old = adapter.snapshot()
    speed = old.lines[0].speed
    assert speed.mode == "KONE" and speed.value == 31.4
    assert speed.sourceTs == first.lines[0].speed.sourceTs
    assert old.lines[0].mode == "KONE" and old.dataMode == "KONE"
    assert old.connection.lastOkTs == first.timestamp


def test_tag_timestamp_older_than_limit_is_kone_on_first_read():
    now = datetime(2026, 10, 18, 13, tzinfo=TM_TZ)
    rows = [{"v": 55000.0, "sourceTs": datetime(2026, 10, 18, 12, 58)}]
    snap = WinCCSqlAdapter(Source(rows), lambda: now, {"fields": [verified("gipsokarton.outputToday")]}).snapshot()
    assert snap.lines[0].outputToday.mode == "KONE"


def test_kone_line_is_not_counted_as_running():
    clock = Clock(datetime(2026, 10, 18, 13, tzinfo=TM_TZ))
    source = Source([{"v": 1}])
    status = verified("gipsokarton.status", values={"1": "RUNNING", "0": "STOPPED"})
    adapter = WinCCSqlAdapter(source, clock, {"fields": [status]})
    client = TestClient(create_app(adapter), client=("127.0.0.1", 50000))
    assert client.get("/api/overview").json()["runningLines"] == 1
    source.fail = True
    clock.now += timedelta(seconds=30)
    body = client.get("/api/overview").json()
    assert body["lines"][0]["status"] == {**body["lines"][0]["status"], "value": "RUNNING", "mode": "KONE"}
    assert body["runningLines"] == 0


def test_status_without_value_table_is_unknown_not_guessed():
    now = datetime(2026, 10, 18, 13, tzinfo=TM_TZ)
    snap = WinCCSqlAdapter(Source([{"v": 1}]), lambda: now, {"fields": [verified("gipsokarton.status")]}).snapshot()
    assert snap.lines[0].status.value == "UNKNOWN"


def test_stream_carries_age_limits_for_client_side_kone(fixed_clock):
    client = TestClient(create_app(DemoAdapter(fixed_clock(13))))
    with client.stream("GET", "/api/stream?limit=1") as resp:
        text = "".join(resp.iter_text())
    assert text.startswith("retry: 3000")
    data = json.loads(text.split("data: ", 1)[1].split("\n", 1)[0])
    assert data["contractVersion"] == API_VERSION and data["connection"]["state"] == "SIMULATED"
    assert data["lines"][0]["speed"]["staleAfterSec"] == 15 and data["lines"][0]["speed"]["sourceTs"]


# --- §7 data rules ---

@pytest.mark.parametrize("a,p,q,expected", [
    (100, 100, 100, 100.0),
    (90, 95, 99, 84.6),
    (85.4, 87.2, 98.6, 73.4),
    (0, 95, 99, 0.0),
    (None, 95, 99, None),
    (90, None, 99, None),
    (90, 95, None, None),
])
def test_oee_vectors(a, p, q, expected):
    assert oee(a, p, q) == expected


def test_oee_is_three_components_not_one_figure(fixed_clock):
    line = DemoAdapter(fixed_clock(13)).snapshot().lines[0]
    assert not hasattr(line, "efficiencyPct")
    c = line.oee
    assert c.oee.value == oee(c.availability.value, c.performance.value, c.quality.value)


def test_shift_output_is_separate_from_daily_output(fixed_clock):
    # 17:00: day started 08:00, shift II started 16:00.
    line = DemoAdapter(fixed_clock(17)).snapshot().lines[0]
    assert 0 < line.shiftOutput.value < line.outputToday.value
    assert line.shiftPlan.value != line.planToday.value


def test_shift_output_crosses_production_day_start(fixed_clock):
    # 08:30 on the 18th: shift III (00:00-08:00) is over, shift I runs since 08:00 = day start.
    line = DemoAdapter(fixed_clock(8, 30)).snapshot().lines[0]
    assert line.shiftOutput.value == pytest.approx(line.outputToday.value)


def test_current_stop_is_measured_from_its_own_start(fixed_clock):
    # Kesiji fault 15:20-15:32; an earlier 18-minute planned stop is in the daily total.
    line = DemoAdapter(fixed_clock(15, 25)).snapshot().lines[0]
    stop = line.currentStop
    assert stop is not None and not stop.planned and stop.durationMin == 5.0
    assert stop.equipmentId == "gipsokarton-06"
    assert line.stopMinutesToday.value > stop.durationMin
    running = DemoAdapter(fixed_clock(13)).snapshot().lines[0]
    assert running.currentStop is None


def test_alarms_sort_by_priority(fixed_clock):
    alarms = DemoAdapter(fixed_clock(21, 20)).snapshot().alarms
    # Active before acknowledged before cleared; inside each state by priority.
    for state in ("ACTIVE", "ACKNOWLEDGED", "CLEARED"):
        group = [a.priority for a in alarms if a.state == state]
        assert group == sorted(group)
    assert all(a.priority == {"CRITICAL": 1, "WARNING": 2, "INFO": 3}[a.severity] for a in alarms)
