from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Iterable, List, Optional, Union


@dataclass
class Rows:
    rows: List[Row] = field(default_factory=list)
    included_tables: List[str] = field(default_factory=list)
    ignore_unspecified: bool = False

    @classmethod
    def coerce_from_unknown(
        cls, unknown: Union[None, Iterable[Row], Rows]
    ) -> Optional[Rows]:
        if isinstance(unknown, Rows):
            return unknown

        if isinstance(unknown, Iterable):
            return Rows().are(*unknown)

        return None

    def __iter__(self):
        for role in self.rows:
            yield role

    def are(self, *rows: Row):
        return replace(self, rows=rows)

    def include_tables(self, *tables: str):
        return replace(self, included_tables=list(tables))


class Row:
    def __init__(self, tablename, **column_values):
        try:
            schema, table = tablename.split(".", 1)
        except ValueError:
            self.schema = None
            self.tablename = tablename
        else:
            self.schema = schema
            self.tablename = table

        self.qualified_name = tablename
        self.column_values = column_values
