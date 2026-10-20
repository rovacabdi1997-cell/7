from adapters.demo import DemoAdapter
from adapters.wincc_sql import AdoExecutor, WinCCSqlAdapter
from app.config import Settings


def build_adapter(settings: Settings):
    if settings.data_source == "demo":
        return DemoAdapter(scenario=settings.demo_scenario)
    if settings.data_source == "wincc":
        executor = AdoExecutor(settings.wincc_connection) if settings.wincc_connection else None
        return WinCCSqlAdapter(executor)
    raise ValueError(f"Unknown DATA_SOURCE: {settings.data_source!r} (use demo or wincc)")
