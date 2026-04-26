import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def iwda_raw() -> dict:
    return json.loads((FIXTURES / "iwda_response.json").read_text())


@pytest.fixture
def emim_raw() -> dict:
    return json.loads((FIXTURES / "emim_response.json").read_text())


@pytest.fixture
def newsapi_raw() -> dict:
    return json.loads((FIXTURES / "newsapi_response.json").read_text())
