import pytest
from fastapi.testclient import TestClient

from app import main
from app.main import app


@pytest.fixture(autouse=True)
def clean_store():
    """각 테스트를 빈 저장소에서 시작한다."""
    main._notes.clear()
    main._next_id = 1
    yield


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def make_note(client):
    def _make(title="첫 노트", body="hello world", tags=None):
        res = client.post(
            "/notes",
            json={"title": title, "body": body, "tags": tags or []},
        )
        assert res.status_code == 201
        return res.json()

    return _make
