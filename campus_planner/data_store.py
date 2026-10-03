from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def save_school_data(path: str | Path, payload: dict[str, Any]) -> Path:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
    return file_path


def load_school_data(path: str | Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    file_path = Path(path)
    if not file_path.exists():
        return default if default is not None else {}

    try:
        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON 格式錯誤: {file_path} -> {exc}") from exc

    if isinstance(data, dict):
        return data

    raise ValueError(f"資料格式預期為 JSON object，實際為 {type(data).__name__}")


def save_records(path: str | Path, records: dict[str, Any]) -> Path:
    return save_school_data(path, records)


def load_records(path: str | Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    return load_school_data(path, default)
