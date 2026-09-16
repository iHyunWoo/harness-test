"""항상 실패하는 테스트.

Harness 테스트 리포트가 실패를 어떻게 보여주는지(메시지, 스택트레이스,
캡처된 출력, FAILURE 와 ERROR 구분) 확인하기 위한 것이다.
파이프라인에서는 별도 스텝으로 돌리고 빌드 판정에서는 제외한다.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.text import excerpt, slugify


@pytest.fixture
def client():
    return TestClient(app)


# 1. 단순 assert 실패 — pytest 가 좌우 값을 나란히 보여준다
def test_simple_assertion():
    assert slugify("Hello World") == "hello_world"


# 2. 자료구조 비교 실패 — 어느 키가 다른지 diff 로 나온다
def test_dict_diff(client):
    res = client.post("/notes", json={"title": "Diff Me", "body": "one two"})
    expected = {
        "id": 1,
        "title": "Diff Me",
        "slug": "diff-me",
        "word_count": 99,
        "reading_time_minutes": 7,
    }
    actual = {k: res.json()[k] for k in expected}
    assert actual == expected


# 3. 깊은 호출 스택에서 예외 — 여러 프레임짜리 트레이스백
def _level_three(value):
    return 100 / value


def _level_two(value):
    return _level_three(value) + 1


def _level_one(value):
    return _level_two(value) * 2


def test_deep_traceback():
    assert _level_one(0) == 1


# 4. 라이브러리 내부에서 터지는 예외 — 앱 코드 밖 프레임까지 보인다
def test_exception_from_app_code():
    excerpt("some text", limit=-5)


# 5. 캡처된 출력이 함께 나오는지
def test_with_captured_output(client):
    print("=== 요청 전 상태 ===")
    print("notes:", client.get("/notes").json())
    res = client.get("/stats")
    print("stats:", res.json())
    print("=== 단언 직전 ===")
    assert res.json()["notes"] == 42


# 6. FAILURE 가 아니라 ERROR 로 분류되는 경우 (픽스처에서 터짐)
@pytest.fixture
def broken_fixture():
    raise RuntimeError("픽스처 준비 중 실패 — 테스트는 실행조차 되지 않는다")


def test_error_not_failure(broken_fixture):
    assert True
