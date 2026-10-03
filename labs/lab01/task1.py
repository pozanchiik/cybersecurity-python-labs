import random
import string
from data.task_condition import criteria, forbidden_passwords, passwords

# Додавання 3 випадкових дублікатів зі списку
for _ in range(3):
    passwords.append(random.choice(passwords))


def run_task1(passwords, criteria, forbidden_passwords):
    """Класифікація паролів за рівнями безпеки."""
    forbidden_set = set(forbidden_passwords)
    special_chars = set(string.punctuation)

    not_allowed_pwd = []
    weak_pwd = []
    medium_pwd = []
    strong_pwd = []
    very_strong_pwd = []

    min_len = criteria["min_length"]

    for pwd in passwords:
        # Заборонені паролі відсікаємо одразу
        if pwd in forbidden_set:
            not_allowed_pwd.append(pwd)
            continue

        # Перевірка базової довжини
        if len(pwd) < min_len:
            weak_pwd.append(pwd)
            continue

        # Перевірка символьних критеріїв
        has_upper = any(char.isupper() for char in pwd)
        has_lower = any(char.islower() for char in pwd)
        has_digit = any(char.isdigit() for char in pwd)
        has_special = any(char in special_chars for char in pwd)

        # Рахуємо кількість виконаних типів символів (від 1 до 4)
        char_types_count = sum([has_upper, has_lower, has_digit, has_special])

        # Чітка градація надійності
        if len(pwd) >= min_len + 4 and char_types_count >= 3:
            very_strong_pwd.append(pwd)
        elif char_types_count >= 3:
            strong_pwd.append(pwd)
        elif char_types_count == 2:
            medium_pwd.append(pwd)
        else:
            weak_pwd.append(pwd)

    print("Заборонені паролі:", ", ".join(not_allowed_pwd) or "немає")
    print("Слабкі паролі:    ", ", ".join(weak_pwd) or "немає")
    print("Середні паролі:   ", ", ".join(medium_pwd) or "немає")
    print("Сильні паролі:    ", ", ".join(strong_pwd) or "немає")
    print("Дуже сильні:      ", ", ".join(very_strong_pwd) or "немає")


run_task1(passwords, criteria, forbidden_passwords)