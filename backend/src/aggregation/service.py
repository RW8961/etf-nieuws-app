import re

from ..etf.client import fetch_etf_holdings
from ..models import AggregatedCompany, NewsArticle
from ..news.client import fetch_news_batch
from ..storage.cache import FileCache


def _slugify(text: str) -> str:
    return re.sub(r"[^\w]", "_", text.lower())


async def get_aggregated_companies(
    etf_ids: list[str],
    cache: FileCache,
    news_api_key: str,
    top_n: int = 10,
    holdings_ttl: int = 86400,
    news_ttl: int = 1800,
    force_refresh: bool = False,
) -> list[AggregatedCompany]:
    from ..models import Holding

    # 1. Fetch / cache holdings per ETF
    all_holdings: list[Holding] = []
    for etf_id in etf_ids:
        cache_key = f"holdings_{etf_id}"
        cached = None if force_refresh else cache.get(cache_key, holdings_ttl)
        if cached is not None:
            holdings = [Holding(**h) for h in cached]
        else:
            holdings = await fetch_etf_holdings(etf_id, top_n)
            cache.set(cache_key, [h.model_dump() for h in holdings])
        all_holdings.extend(holdings)

    # 2. Deduplicate by ticker
    deduped: dict[str, AggregatedCompany] = {}
    for h in all_holdings:
        if h.ticker not in deduped:
            deduped[h.ticker] = AggregatedCompany(
                ticker=h.ticker,
                company_name=h.company_name,
                weight_pct=h.weight_pct,
                etf_sources=[h.etf_source],
                news=[],
            )
        else:
            existing = deduped[h.ticker]
            if h.etf_source not in existing.etf_sources:
                existing.etf_sources.append(h.etf_source)
            existing.weight_pct = max(existing.weight_pct, h.weight_pct)

    companies = list(deduped.values())

    # 3. Fetch news — only batch the cache misses
    misses: list[str] = []
    for company in companies:
        cache_key = f"news_{_slugify(company.company_name)}"
        cached_news = None if force_refresh else cache.get(cache_key, news_ttl)
        if cached_news is not None:
            company.news = [NewsArticle(**a) for a in cached_news]
        else:
            misses.append(company.company_name)

    if misses:
        fresh = await fetch_news_batch(misses, news_api_key)
        for company in companies:
            if company.company_name in fresh:
                company.news = fresh[company.company_name]
                cache.set(
                    f"news_{_slugify(company.company_name)}",
                    [a.model_dump(mode="json") for a in company.news],
                )

    return companies
