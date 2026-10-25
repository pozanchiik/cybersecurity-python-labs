"""Головний модуль FastAPI-застосунку."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from labs.lab03.config import DOMAIN_NAME, THRESHOLD, VAL_UNIT
from labs.lab03.database import initialize_database
from labs.lab03.routers import categories, records
from shared.student import get_student_info


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Контекст життєвого циклу: ініціалізація бази під час запуску."""
    initialize_database()
    yield


app = FastAPI(
    title=f"Lab 3: {DOMAIN_NAME}",
    description=f"Предметна область: {DOMAIN_NAME}. Одиниця вимірювання: {VAL_UNIT}. Поріг небезпеки: {THRESHOLD}.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(categories.router)
app.include_router(records.router)


@app.get("/ping", tags=["System"])
def ping():
    """Перевірка доступності АРІ."""
    return {"status": "ok"}


@app.get("/student", tags=["System"])
def student():
    """Дані про студента з shared/student.py."""
    info = get_student_info()
    return {
        "student_name": info.get("student_name", info.get("pib", "")),
        "group_name": info.get("group_name", info.get("group", "")),
        "variant_number": info.get("variant_number", info.get("variant", 1)),
    }
