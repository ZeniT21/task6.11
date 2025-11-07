import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.main import app


@pytest.fixture(scope="module")
def test_client():
    with TestClient(app) as client:
        yield client
