import asyncio
import warnings
from functools import partial

import yfinance as yf

from ..models import Holding
from .errors import ETFNotFoundError, ETFParseError

ETF_TICKERS: dict[str, str] = {
    "IWDA": "IWDA.L",
    "EMIM": "EMIM.L",
}


def _fetch_holdings_sync(etf_id: str, top_n: int) -> list[Holding]:
    yahoo_ticker = ETF_TICKERS.get(etf_id)
    if not yahoo_ticker:
        raise ETFNotFoundError(f"Unknown ETF: {etf_id}")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            ticker = yf.Ticker(yahoo_ticker)
            df = ticker.funds_data.top_holdings
    except Exception as exc:
        raise ETFParseError(f"Failed to fetch holdings for {etf_id}: {exc}") from exc

    if df is None or df.empty:
        raise ETFParseError(f"No holdings data returned for {etf_id}")

    holdings: list[Holding] = []
    for symbol, row in df.head(top_n).iterrows():
        holdings.append(
            Holding(
                ticker=str(symbol),
                company_name=str(row.get("Name", symbol)),
                weight_pct=round(float(row.get("Holding Percent", 0)) * 100, 4),
                etf_source=etf_id,
            )
        )
    return holdings


async def fetch_etf_holdings(etf_id: str, top_n: int = 10) -> list[Holding]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, partial(_fetch_holdings_sync, etf_id, top_n))
