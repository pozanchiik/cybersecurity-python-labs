"""Модуль початкового заповнення бази даних навчальними даними."""

import json
import logging
import sqlite3
from pathlib import Path

from labs.lab03.database import get_connection, initialize_database

BASE_DIR = Path(__file__).resolve().parent
SEED_PATH = BASE_DIR / "data" / "seed.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_seed_data() -> dict:
    """Прочитати та валідувати вміст seed.json."""
    if not SEED_PATH.exists():
        raise FileNotFoundError(f"Файл {SEED_PATH} не знайдено.")

    with open(SEED_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    categories = data.get("categories", [])
    records = data.get("records", [])

    if len(categories) != 3 or len(records) != 8:
        raise ValueError("seed.json повинен містити рівно 3 категорії та 8 записів.")

    return data


def seed_database() -> None:
    """Заповнити базу даних початковими даними в одній транзакції."""
    initialize_database()

    connection = get_connection()
    try:
        with connection:
            cursor = connection.cursor()

            # Перевірка на наявність даних
            cursor.execute("SELECT COUNT(*) FROM categories")
            count = cursor.fetchone()[0]
            if count > 0:
                print("База даних вже містить дані. Заповнення скасовано.")
                return

            data = load_seed_data()

            # Додавання категорій
            cursor.executemany(
                "INSERT INTO categories (id, name) VALUES (?, ?)",
                [(cat["id"], cat["name"]) for cat in data["categories"]],
            )

            # Додавання записів
            cursor.executemany(
                """
                INSERT INTO records (code, title, category_id, value, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (
                        rec["code"],
                        rec["title"],
                        rec["category_id"],
                        rec["value"],
                        rec["status"],
                    )
                    for rec in data["records"]
                ],
            )
        print("Базу даних успішно заповнено початковими даними.")

    except (sqlite3.IntegrityError, ValueError) as err:
        logger.error(f"Помилка під час заповнення бази даних: {err}")
        print(f"Помилка заповнення: {err}. Зміни скасовано.")
    finally:
        connection.close()


def test_rollback_demo():
    """Демонстрація скасування транзакції при некоректних даних."""
    print("\nДемонстрація rollback")

    # Спроба вставити запис з неіснуючою категорією category_id=999
    bad_data = [
        ("V01-TEST1", "Тест 1", 1, 5.0, "new"),
        ("V01-TEST2", "Тест 2", 999, 5.0, "new"),
    ]

    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.executemany(
                "INSERT INTO records (code, title, category_id, value, status) VALUES (?, ?, ?, ?, ?)",
                bad_data,
            )
    except sqlite3.IntegrityError as err:
        print(f"Виняток SQLite: {err}")
        print("Транзакцію скасовано (rollback). Жоден запис не збережено.")
    finally:
        conn.close()


if __name__ == "__main__":
    seed_database()
    test_rollback_demo()
