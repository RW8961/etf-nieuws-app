from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from config import settings
from ..aggregation.service import get_aggregated_companies
from ..etf.errors import ETFNotFoundError, ETFParseError
from ..news.errors import NewsAPIRateLimitError
from ..storage.cache import make_cache
from .models import ErrorResponse, HoldingsResponse

router = APIRouter()

ETF_IDS = ["IWDA", "EMIM"]

_cache = make_cache(settings.UPSTASH_REDIS_REST_URL, settings.UPSTASH_REDIS_REST_TOKEN, settings.CACHE_DIR)


@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@router.get("/holdings", response_model=HoldingsResponse)
async def get_holdings(force_refresh: bool = Query(default=False)) -> HoldingsResponse:
    try:
        companies = await get_aggregated_companies(
            etf_ids=ETF_IDS,
            cache=_cache,
            news_api_key=settings.NEWS_API_KEY,
            top_n=settings.TOP_N_HOLDINGS,
            holdings_ttl=settings.HOLDINGS_CACHE_TTL,
            news_ttl=settings.NEWS_CACHE_TTL,
            force_refresh=force_refresh,
        )
    except ETFNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ETFParseError as exc:
        raise HTTPException(status_code=502, detail=f"ETF parse error: {exc}")
    except NewsAPIRateLimitError:
        raise HTTPException(status_code=429, detail="NewsAPI rate limit exceeded")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return HoldingsResponse(
        etfs=ETF_IDS,
        generated_at=datetime.now(timezone.utc),
        companies=companies,
    )


@router.get("/holdings/{ticker}", response_model=HoldingsResponse)
async def get_holding_by_ticker(
    ticker: str,
    force_refresh: bool = Query(default=False),
) -> HoldingsResponse:
    try:
        all_companies = await get_aggregated_companies(
            etf_ids=ETF_IDS,
            cache=_cache,
            news_api_key=settings.NEWS_API_KEY,
            top_n=settings.TOP_N_HOLDINGS,
            holdings_ttl=settings.HOLDINGS_CACHE_TTL,
            news_ttl=settings.NEWS_CACHE_TTL,
            force_refresh=force_refresh,
        )
    except (ETFNotFoundError, ETFParseError, NewsAPIRateLimitError, Exception) as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    matches = [c for c in all_companies if c.ticker.upper() == ticker.upper()]
    if not matches:
        raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' not found in top holdings")

    return HoldingsResponse(
        etfs=ETF_IDS,
        generated_at=datetime.now(timezone.utc),
        companies=matches,
    )
