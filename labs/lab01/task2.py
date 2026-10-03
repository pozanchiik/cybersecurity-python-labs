from data.task_condition import (
    blocked_users,
    resources,
    security_levels,
    users,
)


def display_resources(resources, levels):
    """Виводить список усіх ресурсів із їх текстовим рівнем безпеки."""
    print("=== Список ресурсів системи ===")
    for name, level in resources:
        level_name = levels[level - 1]
        print(f"Ресурс: {name:<22} | Рівень безпеки: {level_name}")
    print("=" * 48)


def check_access(username, resource_level, users, blocked_users):
    """Перевіряє доступ користувача до ресурсу відповідно до політики безпеки."""
    if username not in users:
        return "DENY (User not found)"

    if username in blocked_users:
        return "DENY (User is blocked)"

    user_info = users[username]
    if not user_info.get("active", False):
        return "DENY (Account inactive)"

    user_clearance = user_info.get("clearance", 0)
    if user_clearance >= resource_level:
        return "ALLOW"

    return "DENY (Insufficient clearance)"


def run_task2():
    """Головна функція запуску"""
    display_resources(resources, security_levels)

    print("\n=== Результати перевірки доступу ===")
    for username in users:
        for resource_name, resource_level in resources:
            status = check_access(username, resource_level, users, blocked_users)
            print(f"user=[{username}] resource=[{resource_name}] -> {status}")


run_task2()