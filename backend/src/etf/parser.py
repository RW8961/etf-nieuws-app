from ..models import Holding
from .errors import ETFParseError


def _col_index(columns: list[str], name: str) -> int:
    for i, col in enumerate(columns):
        if col.lower() == name.lower():
            return i
    raise ETFParseError(f"Column '{name}' not found in iShares data. Available: {columns}")


def parse_holdings(raw: dict, etf_id: str, top_n: int = 10) -> list[Holding]:
    try:
        table = raw["tableData"]
        columns: list[str] = [col["key"] for col in table["columns"]]
        rows: list[list] = table["data"]
    except (KeyError, TypeError) as exc:
        raise ETFParseError(f"Unexpected iShares JSON structure for {etf_id}: {exc}") from exc

    ticker_idx = _col_index(columns, "ticker")
    name_idx = _col_index(columns, "name")
    weight_idx = _col_index(columns, "weight")

    holdings: list[Holding] = []
    for row in rows:
        ticker = row[ticker_idx]
        # skip cash, derivatives and placeholder rows
        if not ticker or ticker in ("-", "CASH", ""):
            continue
        try:
            weight = float(str(row[weight_idx]).replace(",", ".").replace("%", "").strip())
        except (ValueError, TypeError):
            continue
        holdings.append(
            Holding(
                ticker=ticker,
                company_name=row[name_idx],
                weight_pct=weight,
                etf_source=etf_id,
            )
        )
        if len(holdings) >= top_n:
            break

    return holdings
