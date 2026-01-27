import pytest
from fastapi.testclient import TestClient

from meuhorario.app import app


@pytest.fixture
def client():
    return TestClient(app)
