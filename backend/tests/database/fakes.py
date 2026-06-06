from dataclasses import dataclass
from typing import Any


@dataclass
class FakeResponse:
    data: Any
    count: int | None = None


class FakeQueryBuilder:
    def __init__(self, response: FakeResponse | None) -> None:
        self.response = response
        self.calls: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = []

    def _record(self, name: str, *args: Any, **kwargs: Any) -> "FakeQueryBuilder":
        self.calls.append((name, args, kwargs))
        return self

    def select(self, *args: Any, **kwargs: Any) -> "FakeQueryBuilder":
        return self._record("select", *args, **kwargs)

    def eq(self, *args: Any, **kwargs: Any) -> "FakeQueryBuilder":
        return self._record("eq", *args, **kwargs)

    def gte(self, *args: Any, **kwargs: Any) -> "FakeQueryBuilder":
        return self._record("gte", *args, **kwargs)

    def lte(self, *args: Any, **kwargs: Any) -> "FakeQueryBuilder":
        return self._record("lte", *args, **kwargs)

    def ilike(self, *args: Any, **kwargs: Any) -> "FakeQueryBuilder":
        return self._record("ilike", *args, **kwargs)

    def or_(self, *args: Any, **kwargs: Any) -> "FakeQueryBuilder":
        return self._record("or_", *args, **kwargs)

    def contains(self, *args: Any, **kwargs: Any) -> "FakeQueryBuilder":
        return self._record("contains", *args, **kwargs)

    def order(self, *args: Any, **kwargs: Any) -> "FakeQueryBuilder":
        return self._record("order", *args, **kwargs)

    def range(self, *args: Any, **kwargs: Any) -> "FakeQueryBuilder":
        return self._record("range", *args, **kwargs)

    def maybe_single(self) -> "FakeQueryBuilder":
        return self._record("maybe_single")

    def single(self) -> "FakeQueryBuilder":
        return self._record("single")

    def insert(self, *args: Any, **kwargs: Any) -> "FakeQueryBuilder":
        return self._record("insert", *args, **kwargs)

    def update(self, *args: Any, **kwargs: Any) -> "FakeQueryBuilder":
        return self._record("update", *args, **kwargs)

    def delete(self, *args: Any, **kwargs: Any) -> "FakeQueryBuilder":
        return self._record("delete", *args, **kwargs)

    async def execute(self) -> FakeResponse | None:
        self._record("execute")
        return self.response


class FakeSupabaseClient:
    def __init__(self, builder: FakeQueryBuilder) -> None:
        self.builder = builder
        self.requested_tables: list[str] = []

    def table(self, table_name: str) -> FakeQueryBuilder:
        self.requested_tables.append(table_name)
        return self.builder

    def rpc(
        self,
        function_name: str,
        params: dict[str, Any],
    ) -> FakeQueryBuilder:
        self.requested_tables.append(f"rpc:{function_name}")
        self.builder._record("rpc", function_name, params)
        return self.builder
