import hashlib
import hmac
import os
import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

# Іменована константа для кількості ітерацій хешування
PBKDF2_ITERATIONS = 100_000
# Час дії сеансу в секундах
SESSION_TIMEOUT_SEC = 900


class User:
    def __init__(
        self, username: str, email: str, role: str = "user", active: bool = True
    ):
        self.username = username
        self._email = None
        self.email = email
        self.role = role
        self.active = active
        self.__password_hash = b""
        self.__password_salt = b""

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value: str):
        pattern = r"^[a-zA-Z][a-zA-Z0-9._-]{2,63}@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, value):
            raise ValueError(f"Невірний формат email: {value}")
        self._email = value

    def set_password(self, password: str):
        self.__password_salt = os.urandom(16)
        self.__password_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), self.__password_salt, PBKDF2_ITERATIONS
        )

    def check_password(self, password: str) -> bool:
        if not self.__password_hash or not self.__password_salt:
            return False
        new_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), self.__password_salt, PBKDF2_ITERATIONS
        )
        return hmac.compare_digest(self.__password_hash, new_hash)

    def deactivate(self):
        self.active = False

    def __str__(self):
        return f"User(username='{self.username}', email='{self.email}', role='{self.role}', active={self.active})"


class Admin(User):
    def __init__(
        self,
        username: str,
        email: str,
        active: bool = True,
        permissions: set | None = None,
    ):
        super().__init__(username, email, role="admin", active=active)
        self.permissions = permissions if permissions is not None else set()

    def grant_permission(self, permission: str):
        self.permissions.add(permission)

    def revoke_permission(self, permission: str):
        self.permissions.discard(permission)

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

    def __str__(self):
        return super().__str__() + f" | Permissions: {self.permissions}"


class Session:
    def __init__(self, ip: str):
        self.ip = ip
        now = datetime.now(UTC)
        self.login_time = now
        self.last_activity = now

    def touch(self):
        self.last_activity = datetime.now(UTC)

    def is_active(self, timeout_sec: int) -> bool:
        if timeout_sec <= 0:
            return False
        now = datetime.now(UTC)
        diff = now - self.last_activity
        return diff <= timedelta(seconds=timeout_sec)


@dataclass
class AuditRecord:
    timestamp: datetime
    username: str
    action: str


class AuditLog:
    def __init__(self):
        self.records = []

    def add_log(self, username: str, action: str):
        record = AuditRecord(
            timestamp=datetime.now(UTC), username=username, action=action
        )
        self.records.append(record)

    def show_all(self):
        print("=== Audit Log ===")
        for rec in self.records:
            print(
                f"[{rec.timestamp.isoformat()}] User: '{rec.username}' -> Action: {rec.action}"
            )


class UserAccount:
    def __init__(self, user: User, audit_log: AuditLog = None):
        self.user = user
        self.session = None
        self.audit_log = audit_log if audit_log is not None else AuditLog()

    def login(self, username: str, password: str, ip: str) -> bool:
        if not self.user.active or self.user.username != username:
            self.audit_log.add_log(username, "login_failure")
            return False

        if self.user.check_password(password):
            self.session = Session(ip)
            self.session.touch()
            self.audit_log.add_log(username, "login_success")
            return True
        else:
            self.audit_log.add_log(username, "login_failure")
            return False

    def is_authenticated(self) -> bool:
        return bool(self.session and self.session.is_active(SESSION_TIMEOUT_SEC))

    def logout(self):
        if self.session:
            self.session = None
        self.audit_log.add_log(self.user.username, "logout")

    def __getitem__(self, key):
        if key == "user":
            return self.user
        elif key == "session":
            return self.session
        elif key == "audit_log":
            return self.audit_log
        else:
            raise KeyError(f"Ключ '{key}' не існує або доступ до нього заборонено.")

    def __setitem__(self, key, value):
        if key == "user":
            if not isinstance(value, User):
                raise TypeError("Очікується екземпляр класу User.")
            self.user = value
        elif key == "session":
            if value is not None and not isinstance(value, Session):
                raise TypeError("Очікується екземпляр класу Session або None.")
            self.session = value
        elif key == "audit_log":
            if not isinstance(value, AuditLog):
                raise TypeError("Очікується екземпляр класу AuditLog.")
            self.audit_log = value
        else:
            raise KeyError(f"Модифікація ключа '{key}' заборонена.")
