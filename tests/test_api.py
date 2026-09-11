"""API 통합 테스트."""

import pytest


def test_root(client):
    assert client.get("/").json() == {"message": "harness-test FastAPI app"}


def test_health(client):
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert body["version"]


def test_create_note_derives_fields(client):
    res = client.post("/notes", json={"title": "My First Note", "body": "hello world"})
    assert res.status_code == 201
    note = res.json()
    assert note["id"] == 1
    assert note["slug"] == "my-first-note"
    assert note["word_count"] == 2
    assert note["excerpt"] == "hello world"


@pytest.mark.parametrize(
    "payload",
    [
        {"title": ""},
        {"title": "x" * 121},
        {},
        {"title": "ok", "tags": ["t"] * 11},
        {"title": "ok", "body": 123},
    ],
)
def test_create_note_rejects_invalid(client, payload):
    assert client.post("/notes", json=payload).status_code == 422


def test_get_note(client, make_note):
    created = make_note()
    assert client.get(f"/notes/{created['id']}").json() == created


@pytest.mark.parametrize("note_id", [0, -1, 999])
def test_get_missing_note(client, note_id):
    assert client.get(f"/notes/{note_id}").status_code == 404


def test_patch_updates_only_given_fields(client, make_note):
    created = make_note(title="Original", body="one two three", tags=["a"])
    res = client.patch(f"/notes/{created['id']}", json={"title": "Renamed"})
    assert res.status_code == 200
    updated = res.json()
    assert updated["title"] == "Renamed"
    assert updated["slug"] == "renamed"
    assert updated["body"] == "one two three"
    assert updated["tags"] == ["a"]


def test_patch_recomputes_derived_fields(client, make_note):
    created = make_note(body="one")
    updated = client.patch(f"/notes/{created['id']}", json={"body": "one two three"}).json()
    assert updated["word_count"] == 3


def test_patch_missing_note(client):
    assert client.patch("/notes/999", json={"title": "x"}).status_code == 404


def test_delete_note(client, make_note):
    created = make_note()
    assert client.delete(f"/notes/{created['id']}").status_code == 204
    assert client.get(f"/notes/{created['id']}").status_code == 404


def test_delete_is_not_idempotent(client, make_note):
    created = make_note()
    client.delete(f"/notes/{created['id']}")
    assert client.delete(f"/notes/{created['id']}").status_code == 404


def test_list_filters_by_tag(client, make_note):
    make_note(title="A", tags=["work"])
    make_note(title="B", tags=["home"])
    make_note(title="C", tags=["work", "home"])
    assert len(client.get("/notes", params={"tag": "work"}).json()) == 2


def test_list_filters_by_query(client, make_note):
    make_note(title="Grocery list", body="milk eggs")
    make_note(title="Reading list", body="books")
    assert len(client.get("/notes", params={"q": "list"}).json()) == 2
    assert len(client.get("/notes", params={"q": "milk"}).json()) == 1


def test_list_combines_filters(client, make_note):
    make_note(title="Alpha", body="shared", tags=["x"])
    make_note(title="Beta", body="shared", tags=["y"])
    found = client.get("/notes", params={"tag": "x", "q": "shared"}).json()
    assert len(found) == 1
    assert found[0]["title"] == "Alpha"


def test_stats(client, make_note):
    make_note(title="A", body="one two", tags=["x"])
    make_note(title="B", body="three", tags=["x", "y"])
    assert client.get("/stats").json() == {
        "notes": 2,
        "total_words": 3,
        "distinct_tags": 2,
    }


def test_ids_increment(client, make_note):
    ids = [make_note(title=f"n{i}")["id"] for i in range(3)]
    assert ids == [1, 2, 3]
