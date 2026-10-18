from adapters.demo import DemoAdapter


def lines(snap):
    return {line.id: line for line in snap.lines}


def all_metrics(snap):
    for line in snap.lines:
        for name in ("speed", "outputToday", "planToday", "planToDate", "fulfilmentPct",
                     "efficiencyPct", "stopsToday", "stopMinutesToday", "errorsToday"):
            yield getattr(line, name)
        if line.bagsToday:
            yield line.bagsToday
    yield snap.shift.staffCount


def test_same_clock_gives_same_snapshot(fixed_clock):
    a = DemoAdapter(fixed_clock(13, 7)).snapshot()
    b = DemoAdapter(fixed_clock(13, 7)).snapshot()
    assert a.model_dump() == b.model_dump()


def test_every_value_is_labelled_simulation(fixed_clock):
    snap = DemoAdapter(fixed_clock(13, 7)).snapshot()
    assert snap.dataMode == "SIMULÝASIÝA"
    assert all(m.mode == "SIMULÝASIÝA" for m in all_metrics(snap))
    assert all(a.mode == "SIMULÝASIÝA" for a in snap.alarms)
    assert all(line.mode == "SIMULÝASIÝA" for line in snap.lines)


def test_only_two_production_lines(fixed_clock):
    snap = DemoAdapter(fixed_clock(9)).snapshot()
    assert [line.id for line in snap.lines] == ["gipsokarton", "gury-garyndy"]


def test_fault_window_stops_board_line(fixed_clock):
    board = lines(DemoAdapter(fixed_clock(15, 25)).snapshot())["gipsokarton"]
    assert board.status == "FAULT"
    assert board.speed.value == 0
    assert any(e.name == "Kesiji" and e.status == "FAULT" for e in board.equipment)


def test_planned_stop_is_not_a_fault(fixed_clock):
    board = lines(DemoAdapter(fixed_clock(10, 45)).snapshot())["gipsokarton"]
    assert board.status == "STOPPED"


def test_output_grows_through_the_day(fixed_clock):
    early = lines(DemoAdapter(fixed_clock(9)).snapshot())["gipsokarton"].outputToday.value
    late = lines(DemoAdapter(fixed_clock(17)).snapshot())["gipsokarton"].outputToday.value
    assert 0 < early < late


def test_production_day_starts_at_eight(fixed_clock):
    snap = DemoAdapter(fixed_clock(8, 0)).snapshot()
    board = lines(snap)["gipsokarton"]
    assert board.outputToday.value == 0
    assert snap.productionDayStart.hour == 8


def test_night_belongs_to_previous_production_day(fixed_clock):
    snap = DemoAdapter(fixed_clock(3, 0, day=19)).snapshot()
    assert snap.productionDayStart.day == 18


def test_bags_follow_dry_mix_output(fixed_clock):
    dry = lines(DemoAdapter(fixed_clock(13)).snapshot())["gury-garyndy"]
    expected = int(dry.outputToday.value * 0.92 * 1000 / 25)
    assert abs(dry.bagsToday.value - expected) <= 1
    assert lines(DemoAdapter(fixed_clock(13)).snapshot())["gipsokarton"].bagsToday is None


def test_alarm_states(fixed_clock):
    snap = DemoAdapter(fixed_clock(15, 25)).snapshot()
    cutter = next(a for a in snap.alarms if a.equipment == "Kesiji")
    assert cutter.state == "ACTIVE" and cutter.severity == "CRITICAL"
    paper = next(a for a in snap.alarms if a.equipment == "Kagyz bobinasy")
    assert paper.state == "CLEARED" and paper.durationMin == 18
    assert snap.alarms[0].state != "CLEARED"


def test_future_alarms_are_hidden(fixed_clock):
    snap = DemoAdapter(fixed_clock(9)).snapshot()
    assert all(a.startedAt <= snap.timestamp for a in snap.alarms)


def test_month_total_includes_earlier_days(fixed_clock):
    first = lines(DemoAdapter(fixed_clock(13, day=1)).snapshot())["gipsokarton"]
    assert first.outputMonth.value == first.outputToday.value
    later = lines(DemoAdapter(fixed_clock(13, day=18)).snapshot())["gipsokarton"]
    assert later.outputMonth.value > later.outputToday.value * 10


def test_schedule_lists_all_shifts(fixed_clock):
    assert [s.id for s in DemoAdapter(fixed_clock(13)).snapshot().shift.schedule] == ["I", "II", "III"]


def test_trend_has_one_point_per_elapsed_hour(fixed_clock):
    board = lines(DemoAdapter(fixed_clock(12, 30)).snapshot())["gipsokarton"]
    assert [p.hour for p in board.trend] == ["08:00", "09:00", "10:00", "11:00", "12:00"]
