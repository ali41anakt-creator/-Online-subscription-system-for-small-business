"""Импортируем все модели здесь, чтобы SQLAlchemy зарегистрировал их связи
и Base.metadata знал обо всех таблицах."""
from app.database import Base
from app.models.company import Company
from app.models.customer import Customer
from app.models.plan import BillingCycle, SubscriptionPlan
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.user import User, UserRole

__all__ = [
    "Base",
    "Company",
    "Customer",
    "SubscriptionPlan",
    "BillingCycle",
    "Subscription",
    "SubscriptionStatus",
    "User",
    "UserRole",
]
