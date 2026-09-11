from fastapi import FastAPI, HTTPException, Query

from app.models import HealthResponse, Note, NoteCreate, NoteUpdate
from app.text import excerpt, reading_time_minutes, slugify, word_count

VERSION = "0.1.0"

app = FastAPI(title="harness-test API", version=VERSION)

# 데모용 인메모리 저장소. 프로세스를 재시작하면 초기화된다.
_notes: dict[int, Note] = {}
_next_id = 1


def _build_note(note_id: int, data: NoteCreate) -> Note:
    return Note(
        id=note_id,
        title=data.title,
        body=data.body,
        tags=data.tags,
        slug=slugify(data.title),
        word_count=word_count(data.body),
        reading_time_minutes=reading_time_minutes(data.body),
        excerpt=excerpt(data.body),
    )


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "harness-test FastAPI app"}


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", version=VERSION)


@app.get("/notes", response_model=list[Note])
def list_notes(
    tag: str | None = Query(default=None),
    q: str | None = Query(default=None),
) -> list[Note]:
    notes = list(_notes.values())
    if tag is not None:
        notes = [n for n in notes if tag in n.tags]
    if q is not None:
        needle = q.lower()
        notes = [n for n in notes if needle in n.title.lower() or needle in n.body.lower()]
    return notes


@app.post("/notes", response_model=Note, status_code=201)
def create_note(payload: NoteCreate) -> Note:
    global _next_id
    note = _build_note(_next_id, payload)
    _notes[note.id] = note
    _next_id += 1
    return note


@app.get("/notes/{note_id}", response_model=Note)
def get_note(note_id: int) -> Note:
    note = _notes.get(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@app.patch("/notes/{note_id}", response_model=Note)
def update_note(note_id: int, payload: NoteUpdate) -> Note:
    current = _notes.get(note_id)
    if current is None:
        raise HTTPException(status_code=404, detail="Note not found")

    merged = NoteCreate(
        title=payload.title if payload.title is not None else current.title,
        body=payload.body if payload.body is not None else current.body,
        tags=payload.tags if payload.tags is not None else current.tags,
    )
    updated = _build_note(note_id, merged)
    _notes[note_id] = updated
    return updated


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int) -> None:
    if _notes.pop(note_id, None) is None:
        raise HTTPException(status_code=404, detail="Note not found")


@app.get("/stats")
def stats() -> dict[str, int]:
    return {
        "notes": len(_notes),
        "total_words": sum(n.word_count for n in _notes.values()),
        "distinct_tags": len({t for n in _notes.values() for t in n.tags}),
    }
