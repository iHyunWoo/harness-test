"""노트 본문을 다루는 순수 함수들.

HTTP 없이 단위 테스트할 수 있도록 라우팅과 분리해 둔다.
"""

import math
import re

_SLUG_STRIP = re.compile(r"[^a-z0-9가-힣\s-]")
_SLUG_SPACES = re.compile(r"[\s-]+")


def slugify(title: str) -> str:
    """제목을 URL 조각으로 바꾼다. 빈 결과는 'untitled'."""
    lowered = title.strip().lower()
    cleaned = _SLUG_STRIP.sub("", lowered)
    slug = _SLUG_SPACES.sub("-", cleaned).strip("-")
    return slug or "untitled"


def word_count(body: str) -> int:
    return len(body.split())


def reading_time_minutes(body: str, wpm: int = 200) -> int:
    """분 단위 예상 읽기 시간. 내용이 있으면 최소 1분.

    2.5분짜리 글을 2분에 읽을 수는 없으므로 올림한다.
    round()는 은행가 반올림이라 2.5가 2가 되어 쓰지 않는다.
    """
    if wpm <= 0:
        raise ValueError("wpm must be positive")
    words = word_count(body)
    if words == 0:
        return 0
    return math.ceil(words / wpm)


def excerpt(body: str, limit: int = 80) -> str:
    """limit 자를 넘으면 잘라내고 말줄임표를 붙인다."""
    if limit < 1:
        raise ValueError("limit must be positive")
    collapsed = " ".join(body.split())
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[: limit - 1].rstrip() + "…"
