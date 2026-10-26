"""CAD identity link table and alarm assetId contract.

Rules under test: instances stay separate, name similarity is never evidence, ambiguous rows carry no
target, approvals need a person, alarms link to a machine only through verified configuration."""
import copy
import json
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from adapters.demo import DemoAdapter
from adapters.wincc_sql import WinCCSqlAdapter
from app.config import BASE_DIR, plant_config
from app.main import create_app
from app.timeutil import TM_TZ
from services.cad_identity import build_identity, load_inputs, plant_assets, validate_identity
from services.flow import resolve_asset_id, resolve_asset_key

CAD_DIR = BASE_DIR / "cad"
IDENTITY = json.loads((CAD_DIR / "identity.json").read_text(encoding="utf-8"))
APPROVALS = json.loads((CAD_DIR / "approvals.json").read_text(encoding="utf-8"))
LINKED = ("CANDIDATE", "EVIDENCED", "APPROVED")
INSTANCES = json.loads((CAD_DIR / "instances.json").read_text(encoding="utf-8"))
PLANT = plant_config()


@pytest.fixture
def client(fixed_clock):
    return TestClient(create_app(DemoAdapter(fixed_clock(15, 25))), client=("127.0.0.1", 50000))


def rows_by_code(code):
    return [r for r in IDENTITY["rows"] if r["equipmentCode"] == code]


# ---- table integrity --------------------------------------------------------------------------

def test_table_matches_accepted_model_counts():
    assert IDENTITY["modelRevision"] == "50f09d90d5007baa3d5415e3cf98922f1892f5c17a8c5602fa6410652a6b0bfa"
    assert len(IDENTITY["rows"]) == 513 == INSTANCES["instanceCount"]
    assert len({r["cadInstanceId"] for r in IDENTITY["rows"]}) == 513
    assert IDENTITY["summary"]["uniqueCodes"] == 502
    assert sum(IDENTITY["summary"]["byStatus"].values()) == 513


def test_table_is_valid_and_reproducible():
    assert validate_identity(IDENTITY, PLANT) == []
    rebuilt = load_inputs(CAD_DIR, PLANT)
    assert json.dumps(rebuilt, sort_keys=True) == json.dumps(IDENTITY, sort_keys=True)


def test_same_code_keeps_separate_instances():
    rows = rows_by_code("1-005-510")
    assert len(rows) == 2 and len({r["cadInstanceId"] for r in rows}) == 2
    assert {r["targetAssetId"] for r in rows} == {"gury-garyndy-01"}
    assert {r["cadMarker"] for r in rows} == {"E230", "E231"}


def test_only_rows_in_approvals_file_are_approved_and_carry_a_person():
    approved = [r for r in IDENTITY["rows"] if r["matchStatus"] == "APPROVED"]
    assert {r["cadInstanceId"] for r in approved} == {a["cadInstanceId"] for a in APPROVALS}
    for r in approved:
        assert r["approvedBy"] and r["approvedAt"] and r["revision"] == 2
        assert [e["kind"] for e in r["evidence"]][-1] == "HUMAN_APPROVAL"
    assert all(r["approvedBy"] is None for r in IDENTITY["rows"] if r["matchStatus"] != "APPROVED")


def test_links_come_only_from_explicit_code_matches_or_approved_range_members():
    linked = [r for r in IDENTITY["rows"] if r["matchStatus"] in LINKED]
    exact = {r["cadMarker"]: r["targetAssetId"] for r in linked if r["evidence"][0]["kind"] == "CODE_EXACT"}
    assert exact == {"E230": "gury-garyndy-01", "E231": "gury-garyndy-01", "E295": "gury-garyndy-01",
                     "E302": "gury-garyndy-02", "E307": "gury-garyndy-03", "E311": "gury-garyndy-04"}
    # range members link only through a person: silo bodies approved 2026-10-25
    ranged = [r for r in linked if r["evidence"][0]["kind"] != "CODE_EXACT"]
    assert sorted(r["cadMarker"] for r in ranged) == ["E239", "E240", "E249", "E250", "E259", "E266", "E274", "E281", "E288"]
    assert all(r["evidence"][0]["kind"] == "RANGE_MEMBER_UNVERIFIED" and r["evidence"][-1]["kind"] == "HUMAN_APPROVAL"
               and r["matchStatus"] == "APPROVED" and r["targetAssetId"] == "gury-garyndy-01" for r in ranged)


def test_name_similarity_never_links():
    # "Garyşdyryjy" exists on both lines and CAD has a mixer; only the gury-garyndy code reference links it.
    mixer = rows_by_code("1-005-605")[0]
    assert mixer["targetAssetId"] == "gury-garyndy-03"
    assert not [r for r in IDENTITY["rows"] if (r["targetLineId"] or "") == "gipsokarton"]
    gypsum = [a for a in IDENTITY["assets"] if a["lineId"] == "gipsokarton"]
    assert gypsum and all(a["linkStatus"] == "NO_CAD_CODE_REFERENCE" and not a["cadInstanceIds"] for a in gypsum)


def test_range_members_are_ambiguous_without_target():
    ambiguous = [r for r in IDENTITY["rows"] if r["matchStatus"] == "AMBIGUOUS"]
    assert len(ambiguous) == 54  # 63 range members, 9 silo bodies approved 2026-10-25
    assert all(r["targetAssetId"] is None and r["candidates"] == ["gury-garyndy-01"] for r in ambiguous)
    assert all(r["evidence"][0]["kind"] == "RANGE_MEMBER_UNVERIFIED" for r in ambiguous)
    # the exact endpoints are not part of the ambiguous set
    assert {r["equipmentCode"] for r in ambiguous}.isdisjoint({"1-005-510", "1-005-590"})


def test_assets_missing_from_cad_are_shown_as_such():
    by_id = {a["assetId"]: a for a in IDENTITY["assets"]}
    packer = by_id["gury-garyndy-05"]
    assert packer["linkStatus"] == "CODE_NOT_IN_CAD" and packer["codesInInventoryWithoutCad"] == ["1-005-615"]
    pallet = by_id["gury-garyndy-06"]
    assert pallet["linkStatus"] == "CODE_NOT_IN_CAD" and len(pallet["codesMissingInCad"]) == 3


def test_colliding_codes_on_two_assets_are_ambiguous():
    plant = copy.deepcopy(PLANT)
    plant["lines"]["gipsokarton"]["equipment"][0]["cadCodes"] = ["1-005-605"]
    table = build_identity(INSTANCES, plant)
    row = next(r for r in table["rows"] if r["equipmentCode"] == "1-005-605")
    assert row["matchStatus"] == "AMBIGUOUS" and row["targetAssetId"] is None
    assert sorted(row["candidates"]) == ["gipsokarton-01", "gury-garyndy-03"]


def test_approval_needs_a_listed_candidate_and_a_person():
    ambiguous = next(r for r in IDENTITY["rows"] if r["matchStatus"] == "AMBIGUOUS")
    good = {"cadInstanceId": ambiguous["cadInstanceId"], "targetAssetId": "gury-garyndy-01",
            "approvedBy": "test-person", "approvedAt": "2026-10-24", "basis": "unit test"}
    table = build_identity(INSTANCES, PLANT, [good])
    row = next(r for r in table["rows"] if r["cadInstanceId"] == ambiguous["cadInstanceId"])
    assert row["matchStatus"] == "APPROVED" and row["approvedBy"] == "test-person" and row["revision"] == 2
    assert validate_identity(table, PLANT) == []
    with pytest.raises(ValueError):
        build_identity(INSTANCES, PLANT, [{**good, "targetAssetId": "gipsokarton-02"}])
    with pytest.raises(ValueError):
        build_identity(INSTANCES, PLANT, [{**good, "cadInstanceId": "does-not-exist"}])


def test_validator_flags_unevidenced_links():
    broken = copy.deepcopy(IDENTITY)
    broken["rows"][0].update(matchStatus="CANDIDATE", targetAssetId="gury-garyndy-01", targetAssetKey="cig-mal-silosy",
                             targetLineId="gury-garyndy", evidence=[])
    assert any("without evidence" in p for p in validate_identity(broken, PLANT))


# ---- API --------------------------------------------------------------------------------------

def test_identity_api_and_filters(client):
    body = client.get("/api/cad/identity").json()
    assert len(body["rows"]) == 513
    approved = client.get("/api/cad/identity?status=APPROVED").json()["rows"]
    candidates = client.get("/api/cad/identity?status=CANDIDATE").json()["rows"]
    assert len(approved) == len(APPROVALS) and all(r["matchStatus"] == "APPROVED" for r in approved)
    assert len(approved) + len(candidates) == 15 and all(r["matchStatus"] == "CANDIDATE" for r in candidates)
    assert client.get("/api/cad/identity?status=BOGUS").status_code == 422


def test_identity_asset_endpoint_keeps_one_to_many(client):
    body = client.get("/api/cad/identity/assets/gury-garyndy-01").json()
    assert body["asset"]["name"] == "Çig mal silolary"
    exact = [r for r in body["instances"] if r["matchStatus"] in LINKED]
    assert len(exact) == 12 and len(body["instances"]) == 12 + 54
    assert client.get("/api/cad/identity/assets/yok").status_code == 404


def test_snapshot_exposes_equipment_codes(client):
    snap = client.get("/api/snapshot").json()
    mix = next(l for l in snap["lines"] if l["id"] == "gury-garyndy")
    assert [e["equipmentCodes"] for e in mix["equipment"]][:4] == [["1-005-510", "1-005-590"], ["1-005-600"],
                                                                   ["1-005-605"], ["1-005-610"]]
    board = next(l for l in snap["lines"] if l["id"] == "gipsokarton")
    assert all(e["equipmentCodes"] == [] for e in board["equipment"])
    assert plant_assets(PLANT)[0]["assetId"] == board["equipment"][0]["id"]


# ---- alarm assetId ----------------------------------------------------------------------------

def test_resolver_is_exact_per_line_and_never_guesses():
    assert resolve_asset_id(PLANT, "gipsokarton", "Garyşdyryjy") == "gipsokarton-02"
    assert resolve_asset_id(PLANT, "gury-garyndy", "Garyşdyryjy") == "gury-garyndy-03"
    assert resolve_asset_id(PLANT, "gury-garyndy", "Kesiji") is None  # exists only on the other line
    assert resolve_asset_id(PLANT, "gipsokarton", "garyşdyryjy") is None  # no case/similarity matching
    assert resolve_asset_id(PLANT, "yok", "Garyşdyryjy") is None
    twin = copy.deepcopy(PLANT)
    twin["lines"]["gipsokarton"]["equipment"].append(copy.deepcopy(twin["lines"]["gipsokarton"]["equipment"][1]))
    assert resolve_asset_id(twin, "gipsokarton", "Garyşdyryjy") is None  # same name twice in one line
    assert resolve_asset_id(twin, "gury-garyndy", "Garyşdyryjy") == "gury-garyndy-03"


def test_demo_alarms_carry_the_right_asset(fixed_clock):
    for scenario, hour in (("clock", 23), ("presentation", 13)):
        adapter = DemoAdapter(lambda: datetime(2026, 10, 18, hour, 4, 30, tzinfo=TM_TZ), scenario)
        snap = adapter.snapshot()
        assert snap.alarms
        lines = {l.id: {e.id: e for e in l.equipment} for l in snap.lines}
        for alarm in snap.alarms:
            assert alarm.assetId in lines[alarm.lineId], alarm
            assert lines[alarm.lineId][alarm.assetId].name == alarm.equipment


def test_same_name_on_two_lines_resolves_to_each_own_machine(fixed_clock):
    snap = DemoAdapter(fixed_clock(23, 0)).snapshot()  # Garyşdyryjy faults on gipsokarton at 21:05
    board = next(a for a in snap.alarms if a.lineId == "gipsokarton" and a.equipment == "Garyşdyryjy")
    assert board.assetId == "gipsokarton-02"
    mix = DemoAdapter(lambda: datetime(2026, 10, 18, 14, 10, tzinfo=TM_TZ)).snapshot()
    planned = next(a for a in mix.alarms if a.lineId == "gury-garyndy" and a.equipment == "Garyşdyryjy")
    assert planned.assetId == "gury-garyndy-03"


def test_stream_reconnect_keeps_identity_and_order(client):
    def read():
        with client.stream("GET", "/api/stream?limit=2") as response:
            return [json.loads(l[6:]) for l in "".join(response.iter_text()).splitlines() if l.startswith("data: ")]
    first, second = read(), read()
    seqs = [e["seq"] for e in first + second]
    assert seqs == sorted(seqs) and len(set(seqs)) == 4
    ids = lambda ev: sorted((a["id"], a["assetId"]) for a in ev["alarms"])  # noqa: E731
    assert ids(first[0]) == ids(second[-1]) and any(a[1] for a in ids(first[0]))


class FakeExecutor:
    def __init__(self, rows):
        self.rows = rows

    def query(self, sql):
        return self.rows


def _alarm_field(columns):
    return {"fields": [{"key": "alarms.active", "status": "VERIFIED", "query": "SELECT 1", "lineId": "gury-garyndy",
                        "columns": {"id": "id", "equipment": "equipment", "message": "message", "severity": "severity",
                                    "state": "state", "startedAt": "startedAt", **columns}}]}


def _wincc_alarm(clock, row, columns):
    started = datetime(2026, 10, 18, 9, 0, tzinfo=TM_TZ)
    row = {"id": "A1", "equipment": "Garyşdyryjy", "message": "x", "severity": "CRITICAL", "state": "ACTIVE",
           "startedAt": started, **row}
    return WinCCSqlAdapter(FakeExecutor([row]), clock, _alarm_field(columns)).snapshot().alarms[0]


def test_wincc_alarm_text_alone_never_links(fixed_clock):
    assert _wincc_alarm(fixed_clock(13), {}, {}).assetId is None


def test_wincc_alarm_links_only_through_verified_asset_key(fixed_clock):
    cols = {"assetKey": "assetKey"}
    assert _wincc_alarm(fixed_clock(13), {"assetKey": "garysdyryjy"}, cols).assetId == "gury-garyndy-03"
    assert _wincc_alarm(fixed_clock(13), {"assetKey": "kesiji"}, cols).assetId is None  # not on that line
    assert _wincc_alarm(fixed_clock(13), {"assetKey": ""}, cols).assetId is None
    assert resolve_asset_key(PLANT, "gury-garyndy", "garysdyryjy") == "gury-garyndy-03"
