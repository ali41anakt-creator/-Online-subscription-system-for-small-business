"""Pydantic-схемы подписок. Валидация: end_date строго позже start_date."""
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, model_validator

from app.models.subscription import SubscriptionStatus


class SubscriptionCreate(BaseModel):
    customer_id: int
    plan_id: int
    status: SubscriptionStatus = SubscriptionStatus.trial
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def check_dates(self) -> "SubscriptionCreate":
        if self.end_date <= self.start_date:
            raise ValueError("end_date должна быть строго позже start_date")
        return self


class SubscriptionUpdate(BaseModel):
    plan_id: int | None = None
    status: SubscriptionStatus | None = None
    start_date: date | None = None
    end_date: date | None = None

    @model_validator(mode="after")
    def check_dates(self) -> "SubscriptionUpdate":
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValueError("end_date должна быть строго позже start_date")
        return self


class SubscriptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    plan_id: int
    status: SubscriptionStatus
    start_date: date
    end_date: date
    created_at: datetime
