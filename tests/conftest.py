import sys
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.timeutil import TM_TZ  # noqa: E402


@pytest.fixture
def fixed_clock():
    def make(hour: int, minute: int = 0, day: int = 18):
        return lambda: datetime(2026, 10, day, hour, minute, tzinfo=TM_TZ)
    return make
