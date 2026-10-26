"""Machine states and material flow for one line.

The TV never guesses: which machine runs and where material moves is decided
here, from the line config and the adapter's raw stop information.

- continuous (gypsum board): one stop stops the whole line.
- buffered (dry mix): silos/bunkers decouple the chain; only the segment
  between two buffers around the stopped machine stops.
"""
from datetime import datetime
from typing import Optional

from app.models import DataMode, Equipment, Flow, RunStatus


def equipment_id(line_id: str, order: int) -> str:
    return f"{line_id}-{order:02d}"


def resolve_asset_id(plant: dict, line_id: str, equipment_name: str) -> Optional[str]:
    """Equipment.id for an alarm raised on `equipment_name` of `line_id`, or None.

    Exact name inside the alarm's own line only, and only when that line has exactly one machine
    with the name. The same name on another line never counts; a repeated name inside the line
    returns None instead of picking one."""
    line = plant["lines"].get(line_id)
    if not line:
        return None
    hits = [order for order, e in enumerate(line["equipment"], start=1) if e["name"] == equipment_name]
    return equipment_id(line_id, hits[0]) if len(hits) == 1 else None


def resolve_asset_key(plant: dict, line_id: str, asset_key: str) -> Optional[str]:
    """Equipment.id for a verified `assetKey` column of a real alarm source (unique per line)."""
    line = plant["lines"].get(line_id)
    if not line or not asset_key:
        return None
    hits = [order for order, e in enumerate(line["equipment"], start=1) if e["assetKey"] == asset_key]
    return equipment_id(line_id, hits[0]) if len(hits) == 1 else None


def _segment(chain: list[dict], index: int) -> range:
    """Indexes of the chain segment around `index`, bounded by buffers."""
    if chain[index]["kind"] == "buffer":
        return range(len(chain))
    start = index
    while start > 0 and chain[start - 1]["kind"] != "buffer":
        start -= 1
    end = index
    while end < len(chain) - 1 and chain[end + 1]["kind"] != "buffer":
        end += 1
    return range(start, end + 1)


def machine_states(
    line_cfg: dict,
    stop: Optional[dict],
    mode: DataMode,
) -> dict[str, RunStatus]:
    """Status per assetKey. `stop` is {"equipment": name, "kind": "fault"|"planned"} or None.
    With mode MAGLUMAT_YOK every machine is UNKNOWN: no data never looks like running."""
    items = line_cfg["equipment"]
    if mode == "MAGLUMAT_YOK":
        return {e["assetKey"]: "UNKNOWN" for e in items}
    states: dict[str, RunStatus] = {e["assetKey"]: "RUNNING" for e in items}
    if not stop:
        return states

    source = next((e for e in items if e["name"] == stop["equipment"]), None)
    source_status: RunStatus = "FAULT" if stop["kind"] == "fault" else "STOPPED"
    chain = [e for e in items if e["kind"] != "feed"]

    if line_cfg["flowModel"] == "continuous" or source is None:
        stopped = items
    else:
        if source["kind"] == "feed":
            target = next(i for i, e in enumerate(chain) if e["assetKey"] == source["feedsInto"])
        else:
            target = next(i for i, e in enumerate(chain) if e["assetKey"] == source["assetKey"])
        segment_keys = {chain[i]["assetKey"] for i in _segment(chain, target)}
        stopped = [e for e in items
                   if e["assetKey"] in segment_keys
                   or (e["kind"] == "feed" and e["feedsInto"] in segment_keys)]

    for e in stopped:
        states[e["assetKey"]] = "STOPPED"
    if source is not None:
        states[source["assetKey"]] = source_status
    return states


def build_equipment(line_id: str, line_cfg: dict, states: dict[str, RunStatus], mode: DataMode,
                    source_ts: Optional[datetime] = None) -> list[Equipment]:
    return [
        Equipment(id=equipment_id(line_id, order), name=e["name"], status=states[e["assetKey"]],
                  order=order, assetKey=e["assetKey"], kind=e["kind"], mode=mode, sourceTs=source_ts,
                  ref=e.get("ref", ""), equipmentCodes=list(e.get("cadCodes", [])))
        for order, e in enumerate(line_cfg["equipment"], start=1)
    ]


def build_flow(equipment: list[Equipment], line_cfg: dict, flow_rate: float) -> list[Flow]:
    """Links along the main chain plus feed -> target links. A link carries
    material only when both ends run."""
    by_key = {e.assetKey: e for e in equipment}
    rate = round(max(0.0, min(1.0, flow_rate)), 2)

    def link(a: Equipment, b: Equipment) -> Flow:
        active = a.status == "RUNNING" and b.status == "RUNNING"
        return Flow(fromId=a.id, toId=b.id, active=active, flowRate=rate if active else 0.0)

    chain = [e for e in equipment if e.kind != "feed"]
    links = [link(a, b) for a, b in zip(chain, chain[1:])]
    for cfg in line_cfg["equipment"]:
        if cfg["kind"] == "feed":
            links.append(link(by_key[cfg["assetKey"]], by_key[cfg["feedsInto"]]))
    return links
