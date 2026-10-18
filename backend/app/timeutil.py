from datetime import datetime, timedelta, timezone

# Turkmenistan has no daylight saving time, so a fixed offset is exact.
TM_TZ = timezone(timedelta(hours=5), "Asgabat")


def now_tm() -> datetime:
    return datetime.now(TM_TZ)


def production_day_start(ts: datetime, start_hour: int) -> datetime:
    start = ts.replace(hour=start_hour, minute=0, second=0, microsecond=0)
    return start if ts >= start else start - timedelta(days=1)


def hhmm_to_minutes(value: str) -> int:
    hours, minutes = value.split(":")
    return int(hours) * 60 + int(minutes)
