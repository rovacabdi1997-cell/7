from typing import Optional


def pct(part: Optional[float], whole: Optional[float]) -> Optional[float]:
    if part is None or not whole:
        return None
    return round(part / whole * 100, 1)


def overlap_minutes(start: float, end: float, window_start: float, window_end: float) -> float:
    return max(0.0, min(end, window_end) - max(start, window_start))


def oee(availability: Optional[float], performance: Optional[float], quality: Optional[float]) -> Optional[float]:
    """OEE % = A × P × Q ÷ 10000 (each in %). Unknown when any component is unknown."""
    if availability is None or performance is None or quality is None:
        return None
    return round(availability * performance * quality / 10000, 1)


def nominal_speed(line_cfg: dict) -> float:
    """Nominal speed in the line's rateUnit: m/min for board (m²/h over board width), t/h for dry mix."""
    if "boardWidthM" in line_cfg:
        return line_cfg["nominalPerHour"] / line_cfg["boardWidthM"] / 60
    return line_cfg["nominalPerHour"]
