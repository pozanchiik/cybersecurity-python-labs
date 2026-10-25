"""Інформація про студента, групу та варіант лабораторної роботи."""

# Змінні з даними студента
STUDENT_NAME = "Барановський Максим Михайлович"
GROUP_NAME = "КБ-203"
VARIANT_NUMBER = 1


def get_student_info() -> dict:
    """Повернути словник із даними студента."""
    return {
        "student_name": STUDENT_NAME,
        "group_name": GROUP_NAME,
        "variant_number": VARIANT_NUMBER,
    }