"""Typed JSON data loader with small in-memory caches."""

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.config import get_settings


def _load_json_file(filename: str) -> Any:
    path = get_settings().data_dir / filename
    if not path.exists():
        raise FileNotFoundError(f"Required data file not found: {path}")
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


@lru_cache
def load_schemes() -> dict[str, dict[str, Any]]:
    """Load scheme registry keyed by scheme id."""

    raw = _load_json_file("schemes.json")
    if not isinstance(raw, dict):
        raise ValueError("schemes.json must be an object keyed by scheme id")
    return {key: value for key, value in raw.items() if not key.startswith("_")}


@lru_cache
def load_services() -> list[dict[str, Any]]:
    """Load service catalog."""

    raw = _load_json_file("services.json")
    if not isinstance(raw, list):
        raise ValueError("services.json must be a list")
    return raw


@lru_cache
def load_offices() -> dict[str, Any]:
    """Load district office registry."""

    raw = _load_json_file("offices.json")
    if not isinstance(raw, dict):
        raise ValueError("offices.json must be an object")
    return raw


@lru_cache
def load_portals() -> dict[str, dict[str, Any]]:
    """Load portal registry keyed by portal id."""

    raw = _load_json_file("portals.json")
    if not isinstance(raw, dict):
        raise ValueError("portals.json must be an object")
    return {key: value for key, value in raw.items() if not key.startswith("_")}


def data_file_paths() -> list[Path]:
    """Return JSON files used to build the vector index."""

    return [
        get_settings().data_dir / "schemes.json",
        get_settings().data_dir / "services.json",
        get_settings().data_dir / "offices.json",
        get_settings().data_dir / "portals.json",
    ]

