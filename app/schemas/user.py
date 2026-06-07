"""Pydantic-схемы пользователей и аутентификации (Неделя 4)."""
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserRegister(BaseModel):
    company_id: int
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    role: UserRole = UserRole.employee


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    email: EmailStr
    role: UserRole
    is_active: bool


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
