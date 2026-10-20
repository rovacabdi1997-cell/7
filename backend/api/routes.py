import asyncio
import itertools
import json
import os
from datetime import datetime
from typing import Literal, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import StreamingResponse

from app.config import API_VERSION, plant_config, tag_mapping, tv_config
from app.models import Alarm, Line, ShiftState, Snapshot

router = APIRouter(prefix="/api")


def _snapshot(request: Request) -> Snapshot:
    return request.app.state.adapter.snapshot()


@router.get("/health")
def health(request: Request) -> dict:
    snap = _snapshot(request)
    return {"status": "ok", "version": API_VERSION, "adapter": snap.adapter,
            "dataMode": snap.dataMode, "timestamp": snap.timestamp, "notes": snap.notes}


@router.get("/snapshot", response_model=Snapshot)
def snapshot(request: Request) -> Snapshot:
    return _snapshot(request)


@router.get("/overview")
def overview(request: Request) -> dict:
    snap = _snapshot(request)
    open_alarms = [a for a in snap.alarms if a.state != "CLEARED"]
    return {
        "timestamp": snap.timestamp, "dataMode": snap.dataMode,
        "lines": [line.model_dump(exclude={"trend", "equipment"}) for line in snap.lines],
        "runningLines": sum(1 for line in snap.lines if line.status == "RUNNING"),
        "totalLines": len(snap.lines),
        "alarmCounts": {s: sum(1 for a in open_alarms if a.severity == s) for s in ("CRITICAL", "WARNING", "INFO")},
        "shift": snap.shift,
    }


@router.get("/lines/{line_id}", response_model=Line)
def line(line_id: str, request: Request) -> Line:
    for item in _snapshot(request).lines:
        if item.id == line_id:
            return item
    raise HTTPException(status_code=404, detail=f"Liniýa tapylmady: {line_id}")


@router.get("/alarms", response_model=list[Alarm])
def alarms(request: Request, state: Literal["open", "all"] = "open", line: Optional[str] = None) -> list[Alarm]:
    items = _snapshot(request).alarms
    if state == "open":
        items = [a for a in items if a.state != "CLEARED"]
    if line:
        items = [a for a in items if a.lineId == line]
    return items


@router.get("/shift", response_model=ShiftState)
def shift(request: Request) -> ShiftState:
    return _snapshot(request).shift


@router.get("/mapping")
def mapping(request: Request) -> dict:
    """Tag map of the plant: only from the central PC itself unless MAPPING_REMOTE=1."""
    host = request.client.host if request.client else ""
    if host not in ("127.0.0.1", "::1") and os.getenv("MAPPING_REMOTE") != "1":
        raise HTTPException(status_code=403, detail="Diňe merkez kompýuterden")
    return tag_mapping()


def _default(value):
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(type(value))


# One counter for the whole process: every SSE event gets a unique, rising id.
_seq = itertools.count(1)
PING_SECONDS = 5.0


def _line_snapshot(snap: Snapshot, line_id: Optional[str]) -> Snapshot:
    if not line_id:
        return snap
    return snap.model_copy(update={
        "lines": [x for x in snap.lines if x.id == line_id],
        "alarms": [a for a in snap.alarms if a.lineId == line_id],
    })


@router.get("/stream")
async def stream(request: Request, limit: int = Query(0, ge=0, description="0 = sonsuz; synag üçin"),
                 line: Optional[str] = Query(None, description="gipsokarton | gury-garyndy; boş = iki liniýa")):
    """Server-Sent Events: one snapshot per refresh interval, `: ping` comments in
    between. With `line` the payload carries only that line and its alarms."""
    if line and line not in plant_config()["lines"]:
        raise HTTPException(status_code=404, detail=f"Liniýa tapylmady: {line}")
    settings = request.app.state.settings
    interval = settings.refresh_seconds

    async def events():
        sent = 0
        yield "retry: 3000\n\n"
        while True:
            if await request.is_disconnected():
                break
            seq = next(_seq)
            data = _line_snapshot(_snapshot(request), line).model_dump()
            data.update(seq=seq, staleAfterSec=settings.stale_after_seconds)
            payload = json.dumps(data, default=_default, ensure_ascii=False)
            yield f"id: {seq}\nevent: snapshot\ndata: {payload}\n\n"
            sent += 1
            if limit and sent >= limit:
                break
            waited = 0.0
            while waited < interval:
                step = min(PING_SECONDS, interval - waited)
                await asyncio.sleep(step)
                waited += step
                if waited < interval:
                    yield ": ping\n\n"

    return StreamingResponse(events(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@router.get("/tv/{tv_id}")
def tv(tv_id: str) -> dict:
    """Fixed layout of one factory TV: its line, KPIs and machine order with asset keys."""
    screens = tv_config()
    if tv_id not in screens:
        raise HTTPException(status_code=404, detail=f"TV tapylmady: {tv_id}")
    screen = screens[tv_id]
    line_cfg = plant_config()["lines"][screen["lineId"]]
    machines = [
        {"id": f"{screen['lineId']}-{order:02d}", "order": order, "name": e["name"],
         "assetKey": e["assetKey"], "kind": e["kind"], "feedsInto": e.get("feedsInto"),
         "ref": e.get("ref", "")}
        for order, e in enumerate(line_cfg["equipment"], start=1)
    ]
    return {"tvId": tv_id, **screen, "section": line_cfg["section"], "lineCode": line_cfg["lineCode"],
            "machines": machines, "equipmentSource": line_cfg["equipmentSource"]}
