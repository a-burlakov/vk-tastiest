import string

import pytest
from hypothesis import given
from hypothesis.strategies import text
from fastapi.testclient import TestClient

from backend.core.config import settings


@pytest.mark.parametrize(
    "message, response_message",
    [
        ("test", f"Success! Got message - test."),
        ("test2", f"Success! Got message - test2."),
        ("test3", f"Success! Got message - test3."),
    ],
)
def test_health_check_parametrized(
    client: TestClient, message, response_message
) -> None:
    resp = client.get(f"{settings.API_V1_STR}/utils/health/{message}")
    response = resp.json()

    assert response["msg"] == response_message


@given(text(alphabet=string.ascii_letters, min_size=1))
def test_health_check_hypothesis(client: TestClient, s) -> None:
    resp = client.get(f"{settings.API_V1_STR}/utils/health/{s}")
    response = resp.json()

    assert response["msg"] == f"Success! Got message - {s}."
