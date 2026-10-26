"""Settings and config file loading. Secrets come only from environment variables."""
import json
import os
from functools import lru_cache
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
QUERY_DIR = BASE_DIR.parent / "database" / "readonly_queries"

API_VERSION = "2.1.0"


def load_json(name: str) -> dict:
    return json.loads((CONFIG_DIR / name).read_text(encoding="utf-8"))


@lru_cache
def plant_config() -> dict:
    return load_json("plant.json")


@lru_cache
def tv_config() -> dict:
    return load_json("tv.json")


@lru_cache
def cad_identity() -> dict:
    """Generated CAD instance -> asset link table (scripts/cad/build_identity.py)."""
    return json.loads((BASE_DIR / "cad" / "identity.json").read_text(encoding="utf-8"))


@lru_cache
def tag_mapping() -> dict:
    return load_json("tag_mapping.json")


class Settings:
    def __init__(self) -> None:
        # demo | wincc. There is no automatic fallback between them.
        self.data_source = os.getenv("DATA_SOURCE", "demo").strip().lower()
        self.refresh_seconds = float(os.getenv("REFRESH_SECONDS", "5"))
        # clock = demo follows the production day; presentation = 6-minute fault/recovery loop.
        self.demo_scenario = os.getenv("DEMO_SCENARIO", "clock").strip().lower()
        # A TV shows "Baglanyşyk ýok" when no event arrived for this long.
        self.stale_after_seconds = int(os.getenv("STALE_AFTER_SECONDS", "15"))
        # Example: Provider=WinCCOLEDBProvider.1;Catalog=CC_xxx_R;Data Source=.\WINCC
        self.wincc_connection = os.getenv("WINCC_CONNECTION_STRING", "")
        self.cors_origins = [
            o.strip()
            for o in os.getenv("CORS_ORIGINS", "http://localhost:3010,http://127.0.0.1:3010").split(",")
            if o.strip()
        ]


def get_settings() -> Settings:
    return Settings()
