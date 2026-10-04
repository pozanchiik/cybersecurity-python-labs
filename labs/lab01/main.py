"""Головний модуль для демонстрації виконання Лабораторної роботи №1."""

import os
import sys

# Налаштування шляху для імпорту спільного модуля shared
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from labs.lab01.task1 import run_task1
from labs.lab01.task2 import run_task2
from labs.lab01.task3 import run_task3
from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER


def main():
    """Головна функція для послідовного запуску завдань лабораторної роботи."""
    print("=" * 60)
    print(f"Лабораторна робота №1 | Студент: {STUDENT_NAME}")
    print(f"Група: {GROUP_NAME} | Варіант: {VARIANT_NUMBER}")
    print("=" * 60)

    print("\n--- Завдання 1: Аналізатор надійності паролів ---")
    run_task1()

    print("\n--- Завдання 2: Система контролю доступу ---")
    run_task2()

    print("\n--- Завдання 3: Хешування, CSV-база та логування ---")
    run_task3()

    print("\n" + "=" * 60)
    print("Всі завдання успішно виконані!")
    print("=" * 60)


if __name__ == "__main__":
    main()