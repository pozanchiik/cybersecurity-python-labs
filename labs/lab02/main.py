from datetime import timedelta

from task1 import Admin, User, UserAccount


def demo():
    print("=== Завдання 1 ===")

    # 1. Створення об'єктів та демонстрація прав адміністратора
    print("\n Створення адміністратора та звичайного користувача...")
    admin = Admin("root", "admin@corp.net")
    admin.set_password("AdminPass!1")
    admin.grant_permission("READ_AUDIT")
    admin.grant_permission("DELETE_USERS")
    print(admin)

    user = User("johndoe", "john.d@company.com")
    user.set_password("SecureUser123")
    print(user)

    # 2. Зміна email із валідацією
    print("\n Тестування валідації email...")
    try:
        user.email = "1nvalid_email.com"  # Починається не з букви і не має @
    except ValueError as e:
        print(f"[Успіх перевірки] Зловлено помилку валідації: {e}")

    user.email = "j.doe_updated@company.com"
    print(f"Новий валідний email: {user.email}")

    # 3. Аутентифікація
    print("\n Тестування логіну та створення сесій...")
    account = UserAccount(user)

    print("Спроба входу з неправильним паролем:")
    account.login("johndoe", "WrongPass", "192.168.1.10")
    print(f"Чи аутентифікований? {account.is_authenticated()}")

    print("Спроба входу з правильним паролем:")
    account.login("johndoe", "SecureUser123", "192.168.1.10")
    print(f"Чи аутентифікований? {account.is_authenticated()}")

    # 4. Демонстрація завершення сеансу за таймаутом
    print("\n Імітація завершення часу дії сеансу (timeout)...")
    # Штучно зменшуємо час останньої активності
    account.session.last_activity -= timedelta(seconds=901)
    print(f"Чи аутентифікований після 900+ секунд? {account.is_authenticated()}")

    # 5. Вихід із системи та вивід журналу (демонстрація композиції)
    print("\n Вихід із системи та друк AuditLog...")
    account.logout()

    # Використання __getitem__ для доступу до аудиту
    account["audit_log"].show_all()


# python -m labs.lab02.main demo
def main():
    demo()


if __name__ == "__main__":
    main()
