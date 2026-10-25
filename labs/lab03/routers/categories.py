"""Маршрути для управління категоріями."""

import sqlite3

from fastapi import APIRouter, HTTPException, status

from labs.lab03 import repository
from labs.lab03.schemas import CategoryCreate, CategoryRead

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryRead])
def read_categories():
    """Отримати список усіх категорій."""
    return repository.get_all_categories()


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryCreate):
    """Створити нову категорію."""
    try:
        return repository.create_category(category.name)
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Категорія з назвою '{category.name}' вже існує.",
        )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int):
    """Видалити порожню категорію."""
    if category_id <= 0:
        raise HTTPException(status_code=422, detail="category_id повинен бути > 0")

    cat = repository.get_category_by_id(category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Категорію не знайдено.")

    try:
        success = repository.delete_category(category_id)
        if not success:
            raise HTTPException(status_code=404, detail="Категорію не знайдено.")
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Неможливо видалити категорію, яка містить записи.",
        )
