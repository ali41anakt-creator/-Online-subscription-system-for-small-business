from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.models.user import UserRole

class LoginForm(BaseModel):
    """Форма входа — только email и пароль."""
    email: EmailStr = Field(example="admin@techberry.kz")
    password: str = Field(min_length=6, max_length=128, example="password123")

class UserRegister(BaseModel):
    company_id: int = Field(example=1)
    email: EmailStr = Field(example="new@techberry.kz")
    password: str = Field(min_length=6, max_length=128, example="securepass")
    role: UserRole = Field(default=UserRole.employee)

class UserOut(BaseModel):
    """Пароль никогда не возвращается."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    company_id: int
    email: EmailStr
    role: UserRole
    is_active: bool

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
