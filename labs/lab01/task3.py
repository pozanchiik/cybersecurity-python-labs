import csv
from datetime import datetime
from functools import wraps
import hashlib
import json
import os

from data.task_condition import USERS_TO_REGISTER

MIN_PASSWORD_LENGTH = 12
SALT_VALUE = "00001"

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(CURRENT_DIR, "data")
CSV_PATH = os.path.join(DATA_DIR, "users.csv")
LOG_PATH = os.path.join(DATA_DIR, "log.json")


class ValidationError(Exception):
    """Помилка валідації довжини пароля."""


def generate_hash(password, salt = "00000"):
    """Генерує хеш sha3_512 від конкатенації пароля та солі."""
    if password is None or salt is None or password == "" or salt == "":
        raise ValueError("Пароль та сіль не можуть бути порожніми")

    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError(
            f"Пароль занадто короткий. Мінімум {MIN_PASSWORD_LENGTH} символів."
        )

    data = f"{password}{salt}".encode("utf-8")
    return hashlib.sha3_512(data).hexdigest()


def create_user(username, password):
    """Створює запис користувача з хешованим паролем."""
    hashed_password = generate_hash(password, salt=SALT_VALUE)
    return username, hashed_password


def create_users(users_list):
    """Записує перелік користувачів у CSV-файл бази даних."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CSV_PATH, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["username", "password_hash"])
        for login, pwd in users_list:
            user_entry = create_user(login, pwd)
            writer.writerow(user_entry)


def read_users_db():
    """Зчитує користувачів із файлу CSV."""
    users_db = []
    with open(CSV_PATH, mode="r", newline="", encoding="utf-8") as csv_file:
        reader = csv.reader(csv_file)
        next(reader, None)  # Пропуск заголовка
        for row in reader:
            if len(row) >= 2:
                users_db.append((row[0], row[1]))
    return users_db


def display_users_db(users_db):
    """Виводить вміст бази даних у формі таблиці."""
    print("=" * 86)
    print(f"{'Логін':<20} | {'Хеш пароля (sha3_512, перші 60 симв.)':<62}")
    print("-" * 86)
    for login, pwd_hash in users_db:
        print(f"{login:<20} | {pwd_hash[:60]}...")
    print("=" * 86)


def log_event(func):
    """Декоратор для фіксації подій авторизації у JSON-файл."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        username = kwargs.get("username") if "username" in kwargs else ""
        if not username and args:
            username = args[0]

        result_bool = False
        try:
            result_bool = func(*args, **kwargs)
            return result_bool
        finally:
            log_record = {
                "event": "login",
                "user": str(username),
                "result": "success" if result_bool else "failure",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "args": [str(a) for a in args],
                "kwargs": {k: str(v) for k, v in kwargs.items()},
            }

            records = []
            if os.path.exists(LOG_PATH):
                try:
                    with open(LOG_PATH, mode="r", encoding="utf-8") as jf:
                        records = json.load(jf)
                except (json.JSONDecodeError, IOError):
                    records = []

            records.append(log_record)

            with open(LOG_PATH, mode="w", encoding="utf-8") as jf:
                json.dump(records, jf, indent=4, ensure_ascii=False)

    return wrapper


@log_event
def login(username, password, users_db):
    """Перевіряє автентифікаційні дані користувача."""
    if not username or not password:
        raise ValueError("Ім'я користувача або пароль не можуть бути порожніми")

    input_hash = generate_hash(password, salt=SALT_VALUE)
    for db_user, db_hash in users_db:
        if db_user == username:
            return db_hash == input_hash

    return False


def run_task3():
    try:
        print("1. Створення бази користувачів та збереження у CSV...")
        create_users(USERS_TO_REGISTER)
        print("Базу успішно створено.")

        print("\n2. Зчитування та відображення бази:")
        db = read_users_db()
        display_users_db(db)

        print("\n3. Тестування авторизації та логування:")

        # Успішний вхід
        u1, p1 = "admin_root", "UltraSecur3#Pass2026!"
        res1 = login(u1, p1, db)
        print(f"Вхід [{u1}]: {'Успішно' if res1 else 'Відхилено'}")

        # Неправильний пароль
        u2, p2 = "admin_root", "WrongPassword_123!"
        res2 = login(u2, p2, db)
        print(f"Вхід [{u2}]: {'Успішно' if res2 else 'Відхилено'}")

        # Неіснуючий користувач
        u3, p3 = "unknown_user", "SomeSecurePass123!"
        res3 = login(u3, p3, db)
        print(f"Вхід [{u3}]: {'Успішно' if res3 else 'Відхилено'}")

        print("\n4. Перевірка валідації винятків:")
        try:
            generate_hash("short", salt=SALT_VALUE)
        except ValidationError as err:
            print(f"Очікуваний перехоплений виняток ValidationError: {err}")

        try:
            login("", "some_pwd", db)
        except ValueError as err:
            print(f"Очікуваний перехоплений виняток ValueError: {err}")

        print(f"\nПодії авторизації збережено у: {LOG_PATH}")

    except (FileNotFoundError, PermissionError, IOError) as file_err:
        print(f"Помилка вводу-виводу при роботі з файлами: {file_err}")
    except (ValidationError, ValueError) as val_err:
        print(f"Помилка валідації даних: {val_err}")


if __name__ == "__main__":
    run_task3()