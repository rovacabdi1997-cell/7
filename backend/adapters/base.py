from typing import Protocol

from app.models import Snapshot


class DataAdapter(Protocol):
    """Every data source returns the same Snapshot shape. The dashboard never
    needs to know which adapter is behind the API."""

    name: str

    def snapshot(self) -> Snapshot: ...
