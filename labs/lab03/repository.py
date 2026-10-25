"""Шар доступу до даних (Data Access Layer) для SQLite."""

import sqlite3
from typing import Any

from labs.lab03.database import get_connection

# Операції з категоріями


def get_all_categories() -> list[dict[str, Any]]:
    """Отримати список усіх категорій, відсортованих за id."""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM categories ORDER BY id ASC")
        return [dict(row) for row in cursor.fetchall()]


def get_category_by_id(category_id: int) -> dict[str, Any] | None:
    """Отримати категорію за id."""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM categories WHERE id = ?", (category_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def create_category(name: str) -> dict[str, Any]:
    """Створити нову категорію."""
    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
            cat_id = cursor.lastrowid
            return {"id": cat_id, "name": name}
    finally:
        conn.close()


def delete_category(category_id: int) -> bool:
    """Видалити порожню категорію."""
    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            return cursor.rowcount > 0
    finally:
        conn.close()


# Операції із записами


def get_record_by_id(record_id: int) -> dict[str, Any] | None:
    """Отримати запис за id разом з назвою категорії (JOIN)."""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        query = """
            SELECT r.id, r.code, r.title, r.category_id, c.name AS category_name, r.value, r.status
            FROM records r
            JOIN categories c ON r.category_id = c.id
            WHERE r.id = ?
        """
        cursor.execute(query, (record_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_records(
    category_id: int | None = None,
    status: str | None = None,
    min_value: float | None = None,
    q: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """Отримати список записів."""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = """
            SELECT r.id, r.code, r.title, r.category_id, c.name AS category_name, r.value, r.status
            FROM records r
            JOIN categories c ON r.category_id = c.id
            WHERE 1=1
        """
        params: list[Any] = []

        if category_id is not None:
            query += " AND r.category_id = ?"
            params.append(category_id)

        if status is not None:
            query += " AND r.status = ?"
            params.append(status)

        if min_value is not None:
            query += " AND r.value >= ?"
            params.append(min_value)

        if q is not None:
            query += " AND instr(r.title, ?) > 0"
            params.append(q)

        query += " ORDER BY r.id ASC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def create_record(data: dict[str, Any]) -> dict[str, Any]:
    """Створити новий запис."""
    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO records (code, title, category_id, value, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    data["code"],
                    data["title"],
                    data["category_id"],
                    data["value"],
                    data["status"],
                ),
            )
            rec_id = cursor.lastrowid
        return get_record_by_id(rec_id)
    finally:
        conn.close()


def update_record(record_id: int, data: dict[str, Any]) -> dict[str, Any] | None:
    """Оновити змінювані поля запису."""
    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE records
                SET code = ?, title = ?, category_id = ?, value = ?, status = ?
                WHERE id = ?
                """,
                (
                    data["code"],
                    data["title"],
                    data["category_id"],
                    data["value"],
                    data["status"],
                    record_id,
                ),
            )
            if cursor.rowcount == 0:
                return None
        return get_record_by_id(record_id)
    finally:
        conn.close()


def delete_record(record_id: int) -> bool:
    """Видалити запис за id."""
    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM records WHERE id = ?", (record_id,))
            return cursor.rowcount > 0
    finally:
        conn.close()


def create_records_bulk(records_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Пакетне додавання записів в одній транзакції."""
    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            created_ids = []
            for item in records_data:
                cursor.execute(
                    """
                    INSERT INTO records (code, title, category_id, value, status)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        item["code"],
                        item["title"],
                        item["category_id"],
                        item["value"],
                        item["status"],
                    ),
                )
                created_ids.append(cursor.lastrowid)

        # Читання створених записів
        result = []
        for rec_id in created_ids:
            rec = get_record_by_id(rec_id)
            if rec:
                result.append(rec)
        return result
    finally:
        conn.close()
