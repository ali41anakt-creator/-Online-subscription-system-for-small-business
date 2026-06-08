"""Сложные реляционные запросы (Неделя 4).
Эндпоинт возвращает клиента вместе со всеми его АКТИВНЫМИ подписками и
деталями тарифов через JOIN companies → customers → subscriptions → plans."""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models.customer import Customer
from app.models.plan import SubscriptionPlan
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.user import User

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/customers/{customer_id}/active-subscriptions")
def customer_active_subscriptions(
    customer_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    customer = db.get(Customer, customer_id)
    if customer is None or customer.company_id != user.company_id:
        raise HTTPException(status_code=404, detail="Клиент не найден")

    # JOIN: подписки + тарифы, только активные, для конкретного клиента.
    stmt = (
        select(Subscription, SubscriptionPlan)
        .join(SubscriptionPlan, Subscription.plan_id == SubscriptionPlan.id)
        .where(
            Subscription.customer_id == customer_id,
            Subscription.status == SubscriptionStatus.active,
        )
        .order_by(Subscription.end_date)
    )
    rows = db.execute(stmt).all()

    today = date.today()
    items = [
        {
            "subscription_id": sub.id,
            "status": sub.status.value,
            "start_date": sub.start_date.isoformat(),
            "end_date": sub.end_date.isoformat(),
            "days_remaining": (sub.end_date - today).days,
            "plan": {
                "id": plan.id,
                "name": plan.name,
                "price": float(plan.price),
                "billing_cycle": plan.billing_cycle.value,
            },
        }
        for sub, plan in rows
    ]

    return {
        "customer": {
            "id": customer.id,
            "full_name": customer.full_name,
            "email": customer.email,
        },
        "active_subscriptions_count": len(items),
        "total_monthly_value": round(
            sum(i["plan"]["price"] for i in items), 2
        ),
        "active_subscriptions": items,
    }
