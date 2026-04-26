import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class FileCache:
    def __init__(self, cache_dir: Path) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        safe_key = re.sub(r"[^\w\-]", "_", key)
        return self.cache_dir / f"{safe_key}.json"

    def get(self, key: str, ttl_seconds: int) -> Any | None:
        path = self._path(key)
        if not path.exists():
            return None
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            cached_at = datetime.fromisoformat(raw["cached_at"])
            now = datetime.now(timezone.utc)
            if cached_at.tzinfo is None:
                cached_at = cached_at.replace(tzinfo=timezone.utc)
            age = (now - cached_at).total_seconds()
            if age >= ttl_seconds:
                return None
            return raw["data"]
        except (KeyError, ValueError, json.JSONDecodeError):
            return None

    def set(self, key: str, data: Any) -> None:
        entry = {
            "cached_at": datetime.now(timezone.utc).isoformat(),
            "data": data,
        }
        self._path(key).write_text(
            json.dumps(entry, ensure_ascii=False, default=str),
            encoding="utf-8",
        )
