"""Получение списка всех тарифов. Возвращает чистый JSON через response_model."""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.plan import SubscriptionPlan
from app.schemas.plan import PlanOut

router = APIRouter(prefix="/plans", tags=["Plans"])


@router.get("", response_model=list[PlanOut])
def list_plans(db: Session = Depends(get_db)) -> list[SubscriptionPlan]:
    return list(db.execute(select(SubscriptionPlan)).scalars().all())
