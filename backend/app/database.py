from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable

import app.config as config
from app.config import DATABASE_PATH


_DATE_FIELDS = {"date"}
_DATETIME_FIELDS = {"created_at", "last_updated", "order_date", "recommended_at"}


def _serialize_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return {"__type__": "datetime", "value": value.isoformat()}
    if isinstance(value, date):
        return {"__type__": "date", "value": value.isoformat()}
    if isinstance(value, list):
        return [_serialize_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize_value(item) for key, item in value.items()}
    return value


def _deserialize_value(field: str, value: Any) -> Any:
    if isinstance(value, dict) and value.get("__type__") == "datetime":
        return datetime.fromisoformat(value["value"])
    if isinstance(value, dict) and value.get("__type__") == "date":
        return date.fromisoformat(value["value"])
    if field in _DATE_FIELDS and isinstance(value, str):
        return date.fromisoformat(value)
    if field in _DATETIME_FIELDS and isinstance(value, str):
        return datetime.fromisoformat(value)
    if isinstance(value, list):
        return [_deserialize_value(field, item) for item in value]
    if isinstance(value, dict):
        return {key: _deserialize_value(key, item) for key, item in value.items()}
    return value


class Field:
    def __init__(self, name: str):
        self.name = name

    def __get__(self, instance: Any, owner: Any) -> Any:
        if instance is None:
            return self
        return instance.__dict__.get(self.name)

    def __set__(self, instance: Any, value: Any) -> None:
        instance.__dict__[self.name] = value

    def _condition(self, operator: str, value: Any) -> "Condition":
        return Condition(self.name, operator, value)

    def __eq__(self, value: Any) -> "Condition":
        return self._condition("eq", value)

    def __lt__(self, value: Any) -> "Condition":
        return self._condition("lt", value)

    def __le__(self, value: Any) -> "Condition":
        return self._condition("lte", value)

    def __gt__(self, value: Any) -> "Condition":
        return self._condition("gt", value)

    def __ge__(self, value: Any) -> "Condition":
        return self._condition("gte", value)

    def in_(self, values: Iterable[Any]) -> "Condition":
        return self._condition("in", list(values))

    def asc(self) -> "Sort":
        return Sort(self.name, False)

    def desc(self) -> "Sort":
        return Sort(self.name, True)


@dataclass(frozen=True)
class Condition:
    field: str
    operator: str
    value: Any


@dataclass(frozen=True)
class Sort:
    field: str
    descending: bool


class Document:
    __collection__: str
    id = Field("id")

    def __init__(self, **values: Any):
        for name, value in values.items():
            setattr(self, name, value)

    def to_document(self) -> dict[str, Any]:
        return {
            key: _serialize_value(value)
            for key, value in self.__dict__.items()
            if not key.startswith("_")
        }

    @classmethod
    def from_document(cls, document: dict[str, Any]) -> "Document":
        return cls(**{
            key: _deserialize_value(key, value)
            for key, value in document.items()
        })


def _matches(document: Document, condition: Condition) -> bool:
    actual = getattr(document, condition.field, None)
    expected = condition.value
    if condition.operator == "eq":
        return actual == expected
    if condition.operator == "lt":
        return actual < expected
    if condition.operator == "lte":
        return actual <= expected
    if condition.operator == "gt":
        return actual > expected
    if condition.operator == "gte":
        return actual >= expected
    if condition.operator == "in":
        return actual in expected
    raise ValueError(f"Unsupported query operator: {condition.operator}")


class Query:
    def __init__(self, session: "SQLiteSession", model: type[Document]):
        self.session = session
        self.model = model
        self.conditions: list[Condition] = []
        self.sorts: list[Sort] = []
        self.limit_value: int | None = None

    def filter(self, *conditions: Condition, **values: Any) -> "Query":
        self.conditions.extend(conditions)
        self.conditions.extend(Condition(key, "eq", value) for key, value in values.items())
        return self

    def order_by(self, *sorts: Sort) -> "Query":
        self.sorts = list(sorts)
        return self

    def limit(self, amount: int) -> "Query":
        self.limit_value = amount
        return self

    def _documents(self) -> list[Document]:
        rows = self.session.connection.execute(
            "SELECT payload FROM documents WHERE collection = ?",
            (self.model.__collection__,),
        ).fetchall()
        documents = [
            self.model.from_document(json.loads(row[0]))
            for row in rows
        ]
        for condition in self.conditions:
            documents = [document for document in documents if _matches(document, condition)]
        for sort in reversed(self.sorts):
            def _sort_key(document):
                val = getattr(document, sort.field, None)
                if val is None:
                    return (0, "")
                if isinstance(val, (int, float)):
                    return (1, val)
                if isinstance(val, (datetime, date)):
                    return (2, val.isoformat())
                return (3, str(val))

            documents.sort(
                key=_sort_key,
                reverse=sort.descending,
            )
        if self.limit_value is not None:
            documents = documents[:self.limit_value]
        return documents

    def all(self) -> list[Document]:
        result = self._documents()
        for document in result:
            self.session._track(document)
        return result

    def first(self) -> Document | None:
        result = self.limit(1)._documents()
        if not result:
            return None
        self.session._track(result[0])
        return result[0]

    def count(self) -> int:
        return len(self._documents())


class SQLiteSession:
    def __init__(self, db_path: Path | None = None):
        target_path = db_path or getattr(config, "DATABASE_PATH", DATABASE_PATH)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(target_path, check_same_thread=False)
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                collection TEXT NOT NULL,
                id INTEGER NOT NULL,
                payload TEXT NOT NULL,
                PRIMARY KEY (collection, id)
            )
            """
        )
        self.connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_documents_collection ON documents(collection)"
        )
        self.connection.commit()
        self._tracked: dict[tuple[str, int], Document] = {}
        self._added: list[tuple[str, int]] = []

    def query(self, model: type[Document]) -> Query:
        return Query(self, model)

    def add(self, document: Document) -> None:
        if document.id is None:
            row = self.connection.execute(
                "SELECT COALESCE(MAX(id), 0) + 1 FROM documents WHERE collection = ?",
                (document.__collection__,),
            ).fetchone()
            document.id = row[0]
        self.connection.execute(
            "INSERT INTO documents (collection, id, payload) VALUES (?, ?, ?)",
            (
                document.__collection__,
                document.id,
                json.dumps(document.to_document()),
            ),
        )
        self._added.append((document.__collection__, document.id))
        self._track(document)

    def flush(self) -> None:
        self.connection.commit()

    def commit(self) -> None:
        for document in self._tracked.values():
            self.connection.execute(
                """
                INSERT INTO documents (collection, id, payload) VALUES (?, ?, ?)
                ON CONFLICT(collection, id) DO UPDATE SET payload = excluded.payload
                """,
                (
                    document.__collection__,
                    document.id,
                    json.dumps(document.to_document()),
                ),
            )
        self.connection.commit()
        self._added.clear()

    def rollback(self) -> None:
        self.connection.rollback()
        for collection, document_id in self._added:
            self.connection.execute(
                "DELETE FROM documents WHERE collection = ? AND id = ?",
                (collection, document_id),
            )
        self.connection.commit()
        self._added.clear()

    def close(self) -> None:
        self.connection.close()

    def _track(self, document: Document) -> None:
        self._tracked[(document.__collection__, document.id)] = document


def reset_database(db_path: Path | None = None) -> None:
    target_path = db_path or getattr(config, "DATABASE_PATH", DATABASE_PATH)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(target_path) as connection:
        connection.execute("DROP TABLE IF EXISTS documents")


def get_db():
    db = SQLiteSession()
    try:
        yield db
    finally:
        db.close()


SessionLocal = SQLiteSession
