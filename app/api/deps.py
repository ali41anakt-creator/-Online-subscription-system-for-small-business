import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.core.security import decode_access_token
from app.database import get_db
from app.models.user import User, UserRole

bearer_scheme = HTTPBearer(
    scheme_name="Bearer Token",
    description="Вставьте JWT-токен из ответа /auth/login",
    auto_error=True,
)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    credentials_exc = HTTPException(status_code=401,
        detail="Недействительный или истёкший токен",
        headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exc
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Токен истёк — выполните вход заново",
            headers={"WWW-Authenticate": "Bearer"})
    except jwt.PyJWTError:
        raise credentials_exc
    user = db.get(User, int(user_id))
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Аккаунт деактивирован")
    return user

def require_roles(*roles: UserRole):
    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=403,
                detail=f"Требуется роль: {', '.join(r.value for r in roles)}")
        return user
    return checker
