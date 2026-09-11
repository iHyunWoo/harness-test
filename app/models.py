from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    body: str = Field(default="", max_length=10_000)
    tags: list[str] = Field(default_factory=list, max_length=10)


class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    body: str | None = Field(default=None, max_length=10_000)
    tags: list[str] | None = Field(default=None, max_length=10)


class Note(NoteCreate):
    id: int
    slug: str
    word_count: int
    reading_time_minutes: int
    excerpt: str


class HealthResponse(BaseModel):
    status: str
    version: str
