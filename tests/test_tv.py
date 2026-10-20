"""Two-TV contract: machine states, material flow, line-filtered SSE, TV config."""
import json
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from adapters.demo import DemoAdapter
from adapters.wincc_sql import WinCCSqlAdapter
from app.config import plant_config
from app.main import create_app
from app.timeutil import TM_TZ
from services.flow import machine_states


def _line(snap, line_id):
    return next(x for x in snap.lines if x.id == line_id)


def _states(line):
    return {e.assetKey: e.status for e in line.equipment}


def _flows(line):
    names = {e.id: e.assetKey for e in line.equipment}
    return {(names[f.fromId], names[f.toId]): f for f in line.flow}


def test_running_line_has_active_flow_and_feed_link(fixed_clock):
    board = _line(DemoAdapter(fixed_clock(9)).snapshot(), "gipsokarton")
    assert set(_states(board).values()) == {"RUNNING"}
    flows = _flows(board)
    assert ("kagyz-bobinasy", "formirleme-stoly") in flows
    assert len(flows) == 10  # 9 main-chain links + 1 feed link
    assert all(f.active and 0 < f.flowRate <= 1 for f in flows.values())
    assert [e.order for e in board.equipment] == list(range(1, 12))
    assert all(e.mode == "SIMULÝASIÝA" for e in board.equipment)


def test_continuous_line_stops_everything_on_fault(fixed_clock):
    board = _line(DemoAdapter(fixed_clock(15, 25)).snapshot(), "gipsokarton")
    states = _states(board)
    assert states["kesiji"] == "FAULT"
    assert states["kagyz-bobinasy"] == "STOPPED"
    assert all(s == "STOPPED" for k, s in states.items() if k != "kesiji")
    assert not any(f.active for f in board.flow)
    assert all(f.flowRate == 0 for f in board.flow)


def test_buffered_line_isolates_fault_between_buffers(fixed_clock):
    # Tartym bunkeri fault 01:00-01:20 sits between the raw silos and the product bunker.
    mix = _line(DemoAdapter(fixed_clock(1, 5)).snapshot(), "gury-garyndy")
    states = _states(mix)
    assert states["dozirleyji"] == "FAULT"
    assert states["garysdyryjy"] == "STOPPED"
    assert states["cig-mal-silosy"] == states["tayyar-onum-bunkeri"] == "RUNNING"
    assert states["gaplayjy-masyn"] == states["palet-oruji"] == "RUNNING"
    flows = _flows(mix)
    assert not flows[("cig-mal-silosy", "dozirleyji")].active
    assert not flows[("garysdyryjy", "tayyar-onum-bunkeri")].active
    assert flows[("tayyar-onum-bunkeri", "gaplayjy-masyn")].active
    assert flows[("gaplayjy-masyn", "palet-oruji")].flowRate > 0
    assert next(e for e in mix.equipment if e.assetKey == "garysdyryjy").ref == "1-005-605"


def test_buffered_line_fault_after_bunker_keeps_upstream_running(fixed_clock):
    mix = _line(DemoAdapter(fixed_clock(9, 35)).snapshot(), "gury-garyndy")
    states = _states(mix)
    assert states["gaplayjy-masyn"] == "FAULT"
    assert states["palet-oruji"] == "STOPPED"
    assert states["garysdyryjy"] == "RUNNING"
    assert _flows(mix)[("garysdyryjy", "tayyar-onum-bunkeri")].active


def test_no_data_never_looks_running():
    for line_cfg in plant_config()["lines"].values():
        assert set(machine_states(line_cfg, None, "ÝOK").values()) == {"UNKNOWN"}
    snap = WinCCSqlAdapter(None).snapshot()
    for line in snap.lines:
        assert line.equipment and all(e.status == "UNKNOWN" and e.mode == "ÝOK" for e in line.equipment)
        assert not any(f.active for f in line.flow)


def test_presentation_loop_is_deterministic_and_shows_fault():
    at = lambda m, s: (lambda: datetime(2026, 10, 20, 10, m, s, tzinfo=TM_TZ))
    first = DemoAdapter(at(2, 40), scenario="presentation").snapshot()
    again = DemoAdapter(at(2, 40), scenario="presentation").snapshot()
    assert first.model_dump() == again.model_dump()
    assert _states(_line(first, "gipsokarton"))["kesiji"] == "FAULT"
    assert _line(first, "gury-garyndy").status == "RUNNING"
    assert any(a.id == "SIM-SUNUM-gipsokarton" and a.state == "ACTIVE" for a in first.alarms)
    # Clock-based stops do not happen in the loop, so they raise no alarms.
    assert all(a.id.startswith("SIM-SUNUM") or a.severity == "WARNING" for a in first.alarms)

    later = DemoAdapter(at(3, 40), scenario="presentation").snapshot()
    board = _line(later, "gipsokarton")
    assert board.status == "RUNNING" and 0 < board.flow[0].flowRate < 1  # ramping back up
    mix = _states(_line(later, "gury-garyndy"))
    assert mix["garysdyryjy"] == "FAULT" and mix["dozirleyji"] == "STOPPED"
    assert mix["cig-mal-silosy"] == mix["gaplayjy-masyn"] == "RUNNING"


@pytest.fixture
def client(fixed_clock):
    return TestClient(create_app(DemoAdapter(fixed_clock(9, 35))))


def _events(text):
    return [json.loads(line[6:]) for line in text.splitlines() if line.startswith("data: ")]


def test_stream_filters_one_line_and_numbers_events(client):
    with client.stream("GET", "/api/stream?limit=2&line=gury-garyndy") as response:
        text = "".join(response.iter_text())
    assert text.startswith("retry: 3000")
    events = _events(text)
    assert len(events) == 2
    assert events[1]["seq"] == events[0]["seq"] + 1
    assert all(e["staleAfterSec"] == 15 for e in events)
    assert [x["id"] for x in events[0]["lines"]] == ["gury-garyndy"]
    assert events[0]["alarms"] and all(a["lineId"] == "gury-garyndy" for a in events[0]["alarms"])
    assert f"id: {events[0]['seq']}" in text


def test_stream_without_line_keeps_both_lines(client):
    with client.stream("GET", "/api/stream?limit=1") as response:
        events = _events("".join(response.iter_text()))
    assert len(events[0]["lines"]) == 2


def test_stream_unknown_line_is_404(client):
    assert client.get("/api/stream?line=yok&limit=1").status_code == 404


def test_tv_config(client):
    tv1 = client.get("/api/tv/tv-1").json()
    assert tv1["lineId"] == "gipsokarton" and tv1["lineCode"] == "gk"
    assert len(tv1["machines"]) == 11
    assert [m["assetKey"] for m in tv1["machines"][6:9]] == ["guradyjy", "gyra-kesiji", "bukjalayjy"]
    assert tv1["machines"][10] == {"id": "gipsokarton-11", "order": 11, "name": "Kagyz bobinasy",
                                  "assetKey": "kagyz-bobinasy", "kind": "feed", "feedsInto": "formirleme-stoly",
                                  "ref": "Sanjin 1–5"}
    tv2 = client.get("/api/tv/tv-2").json()
    assert tv2["lineId"] == "gury-garyndy" and len(tv2["machines"]) == 6
    assert [m["ref"] for m in tv2["machines"][1:3]] == ["1-005-600", "1-005-605"]
    assert client.get("/api/tv/tv-9").status_code == 404
