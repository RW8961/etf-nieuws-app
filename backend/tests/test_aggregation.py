import re
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from src.aggregation.service import get_aggregated_companies
from src.models import Holding
from src.storage.cache import FileCache

IWDA_HOLDINGS = [
    Holding(ticker="AAPL", company_name="Apple Inc.", weight_pct=4.67, etf_source="IWDA"),
    Holding(ticker="MSFT", company_name="Microsoft Corp.", weight_pct=3.27, etf_source="IWDA"),
    Holding(ticker="NVDA", company_name="NVIDIA Corp.", weight_pct=5.30, etf_source="IWDA"),
    Holding(ticker="TSM", company_name="Taiwan Semiconductor", weight_pct=1.50, etf_source="IWDA"),
]

EMIM_HOLDINGS = [
    Holding(ticker="TSM", company_name="Taiwan Semiconductor", weight_pct=11.49, etf_source="EMIM"),
    Holding(ticker="005930.KS", company_name="Samsung Electronics", weight_pct=4.37, etf_source="EMIM"),
    Holding(ticker="0700.HK", company_name="Tencent Holdings", weight_pct=3.34, etf_source="EMIM"),
]


@pytest.fixture
def cache(tmp_path: Path) -> FileCache:
    return FileCache(tmp_path / "cache")


@pytest.mark.asyncio
async def test_deduplication_merges_sources(cache: FileCache) -> None:
    side_effect = [IWDA_HOLDINGS, EMIM_HOLDINGS]

    with (
        patch("src.aggregation.service.fetch_etf_holdings", new_callable=AsyncMock, side_effect=side_effect),
        patch("src.aggregation.service.fetch_news_batch", new_callable=AsyncMock, return_value={}),
    ):
        companies = await get_aggregated_companies(["IWDA", "EMIM"], cache, "key")

    tsm = next(c for c in companies if c.ticker == "TSM")
    assert set(tsm.etf_sources) == {"IWDA", "EMIM"}


@pytest.mark.asyncio
async def test_deduplication_keeps_max_weight(cache: FileCache) -> None:
    with (
        patch("src.aggregation.service.fetch_etf_holdings", new_callable=AsyncMock, side_effect=[IWDA_HOLDINGS, EMIM_HOLDINGS]),
        patch("src.aggregation.service.fetch_news_batch", new_callable=AsyncMock, return_value={}),
    ):
        companies = await get_aggregated_companies(["IWDA", "EMIM"], cache, "key")

    tsm = next(c for c in companies if c.ticker == "TSM")
    # EMIM has weight 11.49, IWDA has 1.50 — max should win
    assert tsm.weight_pct == pytest.approx(11.49)


@pytest.mark.asyncio
async def test_news_cache_miss_triggers_fetch(cache: FileCache) -> None:
    mock_batch = AsyncMock(return_value={})
    with (
        patch("src.aggregation.service.fetch_etf_holdings", new_callable=AsyncMock, side_effect=[IWDA_HOLDINGS[:2], EMIM_HOLDINGS[:1]]),
        patch("src.aggregation.service.fetch_news_batch", mock_batch),
    ):
        await get_aggregated_companies(["IWDA", "EMIM"], cache, "key")

    mock_batch.assert_called_once()


@pytest.mark.asyncio
async def test_news_cache_hit_skips_fetch(cache: FileCache) -> None:
    all_holdings = IWDA_HOLDINGS[:2] + EMIM_HOLDINGS[:1]
    for h in all_holdings:
        slug = re.sub(r"[^\w]", "_", h.company_name.lower())
        cache.set(f"news_{slug}", [])

    mock_batch = AsyncMock(return_value={})
    with (
        patch("src.aggregation.service.fetch_etf_holdings", new_callable=AsyncMock, side_effect=[IWDA_HOLDINGS[:2], EMIM_HOLDINGS[:1]]),
        patch("src.aggregation.service.fetch_news_batch", mock_batch),
    ):
        await get_aggregated_companies(["IWDA", "EMIM"], cache, "key")

    mock_batch.assert_not_called()
