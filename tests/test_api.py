import json

import pytest
from fastapi.testclient import TestClient

from adapters.demo import DemoAdapter
from app.main import create_app


@pytest.fixture
def client(fixed_clock):
    return TestClient(create_app(DemoAdapter(fixed_clock(15, 25))), client=("127.0.0.1", 50000))


def test_health(client):
    body = client.get("/api/health").json()
    assert body["status"] == "ok" and body["dataMode"] == "SIMULÝASIÝA"


def test_overview(client):
    body = client.get("/api/overview").json()
    assert body["totalLines"] == 2
    assert body["alarmCounts"]["CRITICAL"] >= 1
    assert "trend" not in body["lines"][0]


def test_line_detail_and_404(client):
    assert client.get("/api/lines/gury-garyndy").json()["unit"] == "t"
    assert client.get("/api/lines/yok").status_code == 404


def test_alarm_filters(client):
    open_alarms = client.get("/api/alarms").json()
    all_alarms = client.get("/api/alarms?state=all").json()
    assert all(a["state"] != "CLEARED" for a in open_alarms)
    assert len(all_alarms) > len(open_alarms)
    assert all(a["lineId"] == "gury-garyndy" for a in client.get("/api/alarms?state=all&line=gury-garyndy").json())


def test_mapping_has_status_for_every_field(client):
    fields = client.get("/api/mapping").json()["fields"]
    assert fields and all(f["status"] in ("VERIFIED", "CANDIDATE", "NO_SOURCE") for f in fields)


def test_stream_sends_snapshot_events(client):
    with client.stream("GET", "/api/stream?limit=1") as response:
        assert response.headers["content-type"].startswith("text/event-stream")
        text = "".join(response.iter_text())
    data = next(line[6:] for line in text.splitlines() if line.startswith("data: "))
    assert json.loads(data)["dataMode"] == "SIMULÝASIÝA"


def test_only_get_is_allowed(client):
    assert client.post("/api/snapshot").status_code == 405


def test_mapping_is_local_only(fixed_clock):
    remote = TestClient(create_app(DemoAdapter(fixed_clock(15, 25))), client=("192.168.1.77", 50000))
    assert remote.get("/api/mapping").status_code == 403
