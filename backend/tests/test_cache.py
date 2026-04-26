import time
from pathlib import Path

import pytest

from src.storage.cache import FileCache


@pytest.fixture
def cache(tmp_path: Path) -> FileCache:
    return FileCache(tmp_path / "cache")


def test_cache_miss_on_empty(cache: FileCache) -> None:
    assert cache.get("missing_key", 3600) is None


def test_cache_hit_within_ttl(cache: FileCache) -> None:
    cache.set("key1", {"value": 42})
    result = cache.get("key1", 3600)
    assert result == {"value": 42}


def test_cache_miss_after_ttl(cache: FileCache) -> None:
    cache.set("key2", {"value": 99})
    # TTL of 0 means immediately expired
    result = cache.get("key2", 0)
    assert result is None


def test_cache_set_creates_file(cache: FileCache) -> None:
    cache.set("key3", [1, 2, 3])
    files = list(cache.cache_dir.glob("*.json"))
    assert len(files) == 1


def test_cache_overwrite(cache: FileCache) -> None:
    cache.set("key4", "first")
    cache.set("key4", "second")
    assert cache.get("key4", 3600) == "second"


def test_cache_special_chars_in_key(cache: FileCache) -> None:
    cache.set("news_apple inc.", {"data": "ok"})
    result = cache.get("news_apple inc.", 3600)
    assert result == {"data": "ok"}
