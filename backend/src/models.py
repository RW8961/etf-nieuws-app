from datetime import datetime
from pydantic import BaseModel


class Holding(BaseModel):
    ticker: str
    company_name: str
    weight_pct: float
    etf_source: str  # "IWDA" | "EMIM"


class NewsArticle(BaseModel):
    title: str
    description: str | None
    url: str
    published_at: datetime
    source_name: str


class AggregatedCompany(BaseModel):
    ticker: str
    company_name: str
    weight_pct: float          # highest weight across ETFs
    etf_sources: list[str]     # e.g. ["IWDA"] or ["IWDA", "EMIM"]
    news: list[NewsArticle]
