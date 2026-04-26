from datetime import datetime
from pydantic import BaseModel

from ..models import AggregatedCompany


class HoldingsResponse(BaseModel):
    etfs: list[str]
    generated_at: datetime
    companies: list[AggregatedCompany]


class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None
