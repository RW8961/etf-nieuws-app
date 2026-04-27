import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx


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
            if (now - cached_at).total_seconds() >= ttl_seconds:
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


class UpstashCache:
    """Persistent cache via Upstash Redis REST API — survives server restarts."""

    _TTL = 86400  # 24 hours

    def __init__(self, url: str, token: str) -> None:
        self.url = url.rstrip("/")
        self._headers = {"Authorization": f"Bearer {token}"}

    def _cmd(self, *args: str) -> Any:
        try:
            r = httpx.post(
                self.url,
                headers=self._headers,
                json=list(args),
                timeout=5.0,
            )
            return r.json().get("result")
        except Exception:
            return None

    def get(self, key: str, ttl_seconds: int) -> Any | None:
        result = self._cmd("GET", key)
        if result is None:
            return None
        try:
            raw = json.loads(result)
            cached_at = datetime.fromisoformat(raw["cached_at"])
            now = datetime.now(timezone.utc)
            if cached_at.tzinfo is None:
                cached_at = cached_at.replace(tzinfo=timezone.utc)
            if (now - cached_at).total_seconds() >= ttl_seconds:
                return None
            return raw["data"]
        except (KeyError, ValueError, json.JSONDecodeError):
            return None

    def set(self, key: str, data: Any) -> None:
        value = json.dumps(
            {"cached_at": datetime.now(timezone.utc).isoformat(), "data": data},
            ensure_ascii=False,
            default=str,
        )
        self._cmd("SET", key, value, "EX", str(self._TTL))


def make_cache(redis_url: str = "", redis_token: str = "", cache_dir: str = ".cache") -> FileCache | UpstashCache:
    if redis_url and redis_token:
        return UpstashCache(redis_url, redis_token)
    return FileCache(Path(cache_dir))
