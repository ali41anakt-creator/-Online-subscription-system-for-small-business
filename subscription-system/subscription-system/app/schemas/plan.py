"""Pydantic-схемы тарифов: вход (create/update) и выход (out)."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.plan import BillingCycle


class PlanCreate(BaseModel):
    company_id: int
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    price: float = Field(ge=0, description="Цена не может быть отрицательной")
    billing_cycle: BillingCycle = BillingCycle.monthly
    is_active: bool = True


class PlanUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    price: float | None = Field(default=None, ge=0)
    billing_cycle: BillingCycle | None = None
    is_active: bool | None = None


class PlanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    name: str
    description: str | None = None
    price: float
    billing_cycle: BillingCycle
    is_active: bool
    created_at: datetime
