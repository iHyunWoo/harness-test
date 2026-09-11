"""순수 함수 단위 테스트. HTTP를 거치지 않는다."""

import pytest

from app.text import excerpt, reading_time_minutes, slugify, word_count


@pytest.mark.parametrize(
    "title,expected",
    [
        ("Hello World", "hello-world"),
        ("  Trim   Me  ", "trim-me"),
        ("Special!@#Chars", "specialchars"),
        ("한글 제목", "한글-제목"),
        ("multiple---dashes", "multiple-dashes"),
        ("!!!", "untitled"),
        ("", "untitled"),
    ],
)
def test_slugify(title, expected):
    assert slugify(title) == expected


@pytest.mark.parametrize(
    "body,expected",
    [("", 0), ("one", 1), ("one two three", 3), ("  spaced   out  ", 2)],
)
def test_word_count(body, expected):
    assert word_count(body) == expected


@pytest.mark.parametrize(
    "words,expected",
    [(0, 0), (1, 1), (100, 1), (200, 1), (400, 2), (500, 3)],
)
def test_reading_time(words, expected):
    assert reading_time_minutes("word " * words) == expected


def test_reading_time_rejects_bad_wpm():
    with pytest.raises(ValueError):
        reading_time_minutes("hello", wpm=0)


def test_excerpt_leaves_short_text_alone():
    assert excerpt("short text", limit=80) == "short text"


def test_excerpt_truncates_and_marks():
    result = excerpt("a" * 200, limit=20)
    assert len(result) == 20
    assert result.endswith("…")


def test_excerpt_collapses_whitespace():
    assert excerpt("a   b \n c") == "a b c"


def test_excerpt_rejects_bad_limit():
    with pytest.raises(ValueError):
        excerpt("hello", limit=0)
