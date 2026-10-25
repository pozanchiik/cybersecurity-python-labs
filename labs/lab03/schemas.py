"""Pydantic-моделі запитів і відповідей (Pydantic v2)."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# Категорії


class CategoryBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    name: str = Field(..., min_length=2, max_length=40)


class CategoryCreate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    id: int = Field(..., gt=0)


# Записи


class RecordCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    code: str = Field(..., min_length=3, max_length=40)
    title: str = Field(..., min_length=3, max_length=120)
    category_id: int = Field(..., gt=0)
    value: float = Field(..., ge=0.0, le=10.0, allow_inf_nan=False)
    status: Literal["new", "in_progress", "done"]


class RecordReplace(RecordCreate):
    pass


class RecordRead(RecordCreate):
    id: int = Field(..., gt=0)
    category_name: str
