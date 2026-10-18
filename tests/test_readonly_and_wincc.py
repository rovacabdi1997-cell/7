from datetime import datetime

import pytest

from adapters.readonly_guard import ReadOnlyViolation, assert_read_only
from adapters.wincc_sql import WinCCSqlAdapter


@pytest.mark.parametrize("query", [
    "SELECT TOP 1 value FROM t",
    "WITH x AS (SELECT 1 AS v) SELECT v FROM x",
    "TAG:R,'Arch\\Speed','0000-00-00 00:10:00.000','0000-00-00 00:00:00.000'",
    "ALARMVIEW:SELECT * FROM AlgViewChs",
])
def test_read_queries_pass(query):
    assert assert_read_only(query)


@pytest.mark.parametrize("query", [
    "UPDATE t SET v = 1",
    "DELETE FROM t",
    "SELECT * INTO copy FROM t",
    "SELECT 1; DROP TABLE t",
    "SELECT 1 -- comment",
    "EXEC sp_who",
    "SELECT * FROM OPENROWSET('x','y','z')",
    "RESTORE DATABASE x FROM DISK='y'",
    "",
])
def test_write_queries_are_rejected(query):
    with pytest.raises(ReadOnlyViolation):
        assert_read_only(query)


class FakeExecutor:
    def __init__(self, rows=None, fail=False):
        self.rows, self.fail, self.calls = rows or [], fail, []

    def query(self, sql):
        self.calls.append(sql)
        if self.fail:
            raise ConnectionError("unreachable")
        return self.rows


def mapping(*fields):
    return {"fields": list(fields)}


def verified(key, query="SELECT v FROM t", **extra):
    return {"key": key, "status": "VERIFIED", "query": query, **extra}


def test_unverified_mapping_returns_empty_not_demo(fixed_clock):
    snap = WinCCSqlAdapter(FakeExecutor(), fixed_clock(13), mapping()).snapshot()
    assert snap.dataMode == "ÝOK"
    board = snap.lines[0]
    assert board.speed.value is None and board.speed.mode == "ÝOK"
    assert snap.alarms == []


def test_candidate_fields_are_never_queried(fixed_clock):
    executor = FakeExecutor([{"v": 1}])
    candidate = {"key": "gipsokarton.speed", "status": "CANDIDATE", "query": "SELECT v FROM t"}
    WinCCSqlAdapter(executor, fixed_clock(13), mapping(candidate)).snapshot()
    assert executor.calls == []


def test_verified_field_is_read_as_real(fixed_clock):
    executor = FakeExecutor([{"v": 31.4}])
    snap = WinCCSqlAdapter(executor, fixed_clock(13), mapping(verified("gipsokarton.speed"))).snapshot()
    assert snap.dataMode == "HAKYKY"
    assert snap.lines[0].speed.value == 31.4 and snap.lines[0].speed.mode == "HAKYKY"
    assert snap.lines[0].outputToday.mode == "ÝOK"


def test_source_failure_reports_without_inventing(fixed_clock):
    adapter = WinCCSqlAdapter(FakeExecutor(fail=True), fixed_clock(13), mapping(verified("gipsokarton.speed")))
    snap = adapter.snapshot()
    assert snap.lines[0].speed.value is None
    assert snap.dataMode == "ÝOK"
    assert any("ConnectionError" in n for n in snap.notes)


def test_write_query_in_mapping_is_blocked(fixed_clock):
    executor = FakeExecutor([{"v": 1}])
    bad = verified("gipsokarton.speed", query="UPDATE t SET v = 0")
    snap = WinCCSqlAdapter(executor, fixed_clock(13), mapping(bad)).snapshot()
    assert executor.calls == []
    assert snap.lines[0].speed.value is None
    assert any("ReadOnlyViolation" in n for n in snap.notes)


def test_alarm_rows_are_mapped(fixed_clock):
    rows = [{"MsgNr": 17, "Text1": "Motor gyzdy", "Text2": "Kesiji", "DateTime": datetime(2026, 10, 18, 12, 30),
             "Class": "critical", "State": "active"}]
    field = verified("alarms.active", query="ALARMVIEW:SELECT * FROM AlgViewChs",
                     columns={"id": "MsgNr", "message": "Text1", "equipment": "Text2",
                              "startedAt": "DateTime", "severity": "Class", "state": "State"})
    snap = WinCCSqlAdapter(FakeExecutor(rows), fixed_clock(13), mapping(field)).snapshot()
    assert len(snap.alarms) == 1
    alarm = snap.alarms[0]
    assert alarm.severity == "CRITICAL" and alarm.mode == "HAKYKY" and alarm.durationMin == 30
