import pytest
import httpx
from pytest_httpx import HTTPXMock

from src.news.client import fetch_news_for_company, fetch_news_batch
from src.news.errors import NewsAPIRateLimitError


@pytest.mark.asyncio
async def test_fetch_news_returns_articles(httpx_mock: HTTPXMock, newsapi_raw: dict) -> None:
    httpx_mock.add_response(json=newsapi_raw)
    async with httpx.AsyncClient() as client:
        articles = await fetch_news_for_company("Apple Inc.", "test_key", client)
    assert len(articles) == 2
    assert articles[0].title == "Apple reports record quarterly revenue"
    assert articles[0].source_name == "Reuters"


@pytest.mark.asyncio
async def test_fetch_news_raises_on_rate_limit(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(status_code=429)
    async with httpx.AsyncClient() as client:
        with pytest.raises(NewsAPIRateLimitError):
            await fetch_news_for_company("Apple Inc.", "test_key", client)


@pytest.mark.asyncio
async def test_batch_continues_on_single_failure(httpx_mock: HTTPXMock, newsapi_raw: dict) -> None:
    # First company gets a 429, second succeeds
    httpx_mock.add_response(status_code=429)
    httpx_mock.add_response(json=newsapi_raw)

    result = await fetch_news_batch(["Apple Inc.", "Microsoft Corp."], "test_key")

    assert result["Apple Inc."] == []
    assert len(result["Microsoft Corp."]) == 2


@pytest.mark.asyncio
async def test_fetch_news_empty_articles(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(json={"status": "ok", "totalResults": 0, "articles": []})
    async with httpx.AsyncClient() as client:
        articles = await fetch_news_for_company("Unknown Corp.", "test_key", client)
    assert articles == []
