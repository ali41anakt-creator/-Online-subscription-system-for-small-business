"""CRUD подписок (Неделя 3) + RBAC (Неделя 4).
По требованию: удалять подписку может только admin, обновлять — admin или employee."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.database import get_db
from app.models.customer import Customer
from app.models.plan import SubscriptionPlan
from app.models.subscription import Subscription
from app.models.user import User, UserRole
from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionOut,
    SubscriptionUpdate,
)

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


def _customer_in_company(customer_id: int, company_id: int, db: Session) -> Customer:
    customer = db.get(Customer, customer_id)
    if customer is None or customer.company_id != company_id:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    return customer


def _plan_in_company(plan_id: int, company_id: int, db: Session) -> SubscriptionPlan:
    plan = db.get(SubscriptionPlan, plan_id)
    if plan is None or plan.company_id != company_id:
        raise HTTPException(status_code=404, detail="Тариф не найден")
    return plan


def _get_owned_subscription(sub_id: int, company_id: int, db: Session) -> Subscription:
    sub = db.get(Subscription, sub_id)
    if sub is None:
        raise HTTPException(status_code=404, detail="Подписка не найдена")
    # Проверяем принадлежность подписки компании через клиента.
    if sub.customer is None or sub.customer.company_id != company_id:
        raise HTTPException(status_code=404, detail="Подписка не найдена")
    return sub


@router.get("", response_model=list[SubscriptionOut])
def list_subscriptions(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> list[Subscription]:
    stmt = (
        select(Subscription)
        .join(Customer, Subscription.customer_id == Customer.id)
        .where(Customer.company_id == user.company_id)
    )
    return list(db.execute(stmt).scalars().all())


@router.get("/{subscription_id}", response_model=SubscriptionOut)
def get_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Subscription:
    return _get_owned_subscription(subscription_id, user.company_id, db)


@router.post("", response_model=SubscriptionOut, status_code=status.HTTP_201_CREATED)
def create_subscription(
    payload: SubscriptionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.employee)),
) -> Subscription:
    # Валидируем существование и принадлежность клиента и тарифа.
    _customer_in_company(payload.customer_id, user.company_id, db)
    _plan_in_company(payload.plan_id, user.company_id, db)

    sub = Subscription(**payload.model_dump())
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


@router.put("/{subscription_id}", response_model=SubscriptionOut)
def update_subscription(
    subscription_id: int,
    payload: SubscriptionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.employee)),
) -> Subscription:
    sub = _get_owned_subscription(subscription_id, user.company_id, db)
    data = payload.model_dump(exclude_unset=True)

    if "plan_id" in data:
        _plan_in_company(data["plan_id"], user.company_id, db)

    for field, value in data.items():
        setattr(sub, field, value)

    # Проверка дат после применения частичного обновления.
    if sub.end_date <= sub.start_date:
        raise HTTPException(
            status_code=400, detail="end_date должна быть строго позже start_date"
        )

    db.commit()
    db.refresh(sub)
    return sub


@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin)),  # только admin
) -> None:
    sub = _get_owned_subscription(subscription_id, user.company_id, db)
    db.delete(sub)
    db.commit()
