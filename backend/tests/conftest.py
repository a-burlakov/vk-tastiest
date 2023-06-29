from typing import Generator
import pytest
from fastapi.testclient import TestClient
from aioresponses import aioresponses

from backend.main import app


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def mock_aioresponse():
    with aioresponses() as m:
        yield m
