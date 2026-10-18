import asyncio
import json
from datetime import datetime
from typing import Literal, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import StreamingResponse

from app.config import API_VERSION, tag_mapping
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
def mapping() -> dict:
    return tag_mapping()


def _default(value):
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(type(value))


@router.get("/stream")
async def stream(request: Request, limit: int = Query(0, ge=0, description="0 = sonsuz; synag üçin")):
    """Server-Sent Events: one full snapshot per refresh interval."""
    interval = request.app.state.settings.refresh_seconds

    async def events():
        sent = 0
        while True:
            if await request.is_disconnected():
                break
            payload = json.dumps(_snapshot(request).model_dump(), default=_default, ensure_ascii=False)
            yield f"event: snapshot\ndata: {payload}\n\n"
            sent += 1
            if limit and sent >= limit:
                break
            await asyncio.sleep(interval)

    return StreamingResponse(events(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
