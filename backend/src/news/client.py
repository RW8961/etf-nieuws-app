import asyncio
import logging
from datetime import datetime, timedelta, timezone

import httpx

from ..models import NewsArticle
from .errors import NewsAPIError, NewsAPIRateLimitError

_BASE_URL = "https://newsapi.org/v2/everything"
logger = logging.getLogger(__name__)


def _parse_article(raw: dict) -> NewsArticle:
    return NewsArticle(
        title=raw.get("title") or "",
        description=raw.get("description"),
        url=raw.get("url") or "",
        published_at=datetime.fromisoformat(
            (raw.get("publishedAt") or "").replace("Z", "+00:00")
        ),
        source_name=(raw.get("source") or {}).get("name") or "",
    )


async def fetch_news_for_company(
    company_name: str,
    api_key: str,
    client: httpx.AsyncClient,
    page_size: int = 5,
    lookback_hours: int = 72,
) -> list[NewsArticle]:
    from_dt = (
        datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
    ).strftime("%Y-%m-%dT%H:%M:%SZ")
    params = {
        "q": f'"{company_name}"',
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": page_size,
        "from": from_dt,
        "apiKey": api_key,
    }
    response = await client.get(_BASE_URL, params=params, timeout=15.0)
    if response.status_code == 429:
        raise NewsAPIRateLimitError("NewsAPI rate limit exceeded")
    if response.status_code != 200:
        raise NewsAPIError(f"NewsAPI returned {response.status_code} for '{company_name}'")
    data = response.json()
    articles = data.get("articles") or []
    result = []
    for a in articles:
        try:
            result.append(_parse_article(a))
        except Exception:
            continue
    return result


async def fetch_news_batch(
    companies: list[str],
    api_key: str,
    page_size: int = 5,
    lookback_hours: int = 72,
) -> dict[str, list[NewsArticle]]:
    async with httpx.AsyncClient() as client:
        tasks = [
            fetch_news_for_company(name, api_key, client, page_size, lookback_hours)
            for name in companies
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    output: dict[str, list[NewsArticle]] = {}
    for name, result in zip(companies, results):
        if isinstance(result, Exception):
            logger.warning("News fetch failed for '%s': %s", name, result)
            output[name] = []
        else:
            output[name] = result
    return output
