from app.config import plant_config
from services.shifts import shift_state


def at(fixed_clock, hour, minute=0):
    return shift_state(plant_config()["shifts"], fixed_clock(hour, minute)())


def test_morning_shift(fixed_clock):
    state = at(fixed_clock, 9, 30)
    assert state["current"]["id"] == "I"
    assert state["next"]["id"] == "II"
    assert state["elapsedMin"] == 90 and state["remainingMin"] == 390


def test_shift_ending_at_midnight(fixed_clock):
    state = at(fixed_clock, 23, 50)
    assert state["current"]["id"] == "II"
    assert state["remainingMin"] == 10


def test_night_shift_and_wraparound(fixed_clock):
    state = at(fixed_clock, 0, 0)
    assert state["current"]["id"] == "III"
    assert state["next"]["id"] == "I"


def test_break(fixed_clock):
    assert at(fixed_clock, 12, 10)["onBreak"] is True
    assert at(fixed_clock, 12, 40)["onBreak"] is False
