import pytest

from app.database.queries.common import Pagination, sanitize_search_term


def test_pagination_calculates_inclusive_range() -> None:
    pagination = Pagination(page=3, page_size=25)

    assert pagination.range_start == 50
    assert pagination.range_end == 74


@pytest.mark.parametrize(
    ("page", "page_size"),
    [
        (0, 20),
        (1, 0),
        (1, 101),
    ],
)
def test_pagination_rejects_invalid_values(page: int, page_size: int) -> None:
    with pytest.raises(ValueError):
        Pagination(page=page, page_size=page_size)


def test_search_term_removes_postgrest_control_characters() -> None:
    assert sanitize_search_term("  Maya,(Chen)%  ") == "MayaChen"
