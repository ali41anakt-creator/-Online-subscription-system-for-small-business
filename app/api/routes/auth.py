from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.security import create_access_token, hash_password, verify_password
from app.database import get_db
from app.models.user import User
from app.schemas.user import LoginForm, Token, UserOut, UserRegister

router = APIRouter(prefix="/auth", tags=["Аутентификация"])

@router.post("/register", response_model=UserOut, status_code=201,
    summary="Регистрация пользователя",
    responses={400: {"description": "Email уже зарегистрирован"}})
def register(payload: UserRegister, db: Session = Depends(get_db)) -> User:
    existing = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    user = User(company_id=payload.company_id, email=payload.email,
                hashed_password=hash_password(payload.password), role=payload.role)
    db.add(user); db.commit(); db.refresh(user)
    return user

@router.post("/login", response_model=Token, summary="Вход и получение JWT-токена",
    responses={401: {"description": "Неверный email или пароль"}})
def login(form: LoginForm, db: Session = Depends(get_db)) -> Token:
    user = db.execute(select(User).where(User.email == form.email)).scalar_one_or_none()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    token = create_access_token(subject=str(user.id), role=user.role.value, company_id=user.company_id)
    return Token(access_token=token)
