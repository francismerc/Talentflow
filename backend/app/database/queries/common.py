import re
from dataclasses import dataclass

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
MAX_SEARCH_LENGTH = 100

_UNSAFE_SEARCH_CHARACTERS = re.compile(r"[^\w\s@.+-]", re.UNICODE)


@dataclass(frozen=True, slots=True)
class Pagination:
    page: int = 1
    page_size: int = DEFAULT_PAGE_SIZE

    def __post_init__(self) -> None:
        if self.page < 1:
            raise ValueError("page must be greater than or equal to 1")
        if not 1 <= self.page_size <= MAX_PAGE_SIZE:
            raise ValueError(f"page_size must be between 1 and {MAX_PAGE_SIZE}")

    @property
    def range_start(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def range_end(self) -> int:
        return self.range_start + self.page_size - 1


@dataclass(frozen=True, slots=True)
class QueryPage[RecordT]:
    items: list[RecordT]
    page: int
    page_size: int
    total: int


def sanitize_search_term(value: str | None) -> str | None:
    """Normalize text before placing it into PostgREST filter syntax."""
    if value is None:
        return None

    normalized = " ".join(value.strip().split())
    normalized = _UNSAFE_SEARCH_CHARACTERS.sub("", normalized)
    return normalized[:MAX_SEARCH_LENGTH] or None
