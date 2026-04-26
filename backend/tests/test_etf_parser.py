import pytest

from src.etf.errors import ETFParseError
from src.etf.parser import parse_holdings


def test_parse_holdings_extracts_top_10(iwda_raw: dict) -> None:
    holdings = parse_holdings(iwda_raw, "IWDA", top_n=10)
    assert len(holdings) == 10


def test_parse_holdings_correct_fields(iwda_raw: dict) -> None:
    holdings = parse_holdings(iwda_raw, "IWDA")
    first = holdings[0]
    assert first.ticker == "AAPL"
    assert first.company_name == "Apple Inc."
    assert first.weight_pct == pytest.approx(4.23)
    assert first.etf_source == "IWDA"


def test_parse_holdings_etf_source_set(emim_raw: dict) -> None:
    holdings = parse_holdings(emim_raw, "EMIM")
    assert all(h.etf_source == "EMIM" for h in holdings)


def test_parse_holdings_top_n_limit(iwda_raw: dict) -> None:
    holdings = parse_holdings(iwda_raw, "IWDA", top_n=3)
    assert len(holdings) == 3


def test_parse_holdings_raises_on_missing_column(iwda_raw: dict) -> None:
    # Remove the 'weight' column
    iwda_raw["tableData"]["columns"] = [
        {"key": "ticker", "display": "Ticker"},
        {"key": "name", "display": "Name"},
    ]
    with pytest.raises(ETFParseError):
        parse_holdings(iwda_raw, "IWDA")


def test_parse_holdings_raises_on_bad_structure() -> None:
    with pytest.raises(ETFParseError):
        parse_holdings({"unexpected": "structure"}, "IWDA")
