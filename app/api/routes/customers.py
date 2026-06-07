"""CRUD клиентов (Неделя 3) + RBAC (Неделя 4).
Чтение — любой авторизованный; создание/изменение — admin/employee; удаление — только admin."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.database import get_db
from app.models.customer import Customer
from app.models.user import User, UserRole
from app.schemas.customer import CustomerCreate, CustomerOut, CustomerUpdate

router = APIRouter(prefix="/customers", tags=["Customers"])


def _get_owned_customer(customer_id: int, company_id: int, db: Session) -> Customer:
    customer = db.get(Customer, customer_id)
    if customer is None or customer.company_id != company_id:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    return customer


@router.get("", response_model=list[CustomerOut])
def list_customers(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> list[Customer]:
    return list(
        db.execute(
            select(Customer).where(Customer.company_id == user.company_id)
        ).scalars().all()
    )


@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Customer:
    return _get_owned_customer(customer_id, user.company_id, db)


@router.post("", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
def create_customer(
    payload: CustomerCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.employee)),
) -> Customer:
    customer = Customer(**payload.model_dump())
    db.add(customer)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Клиент с таким email уже существует в компании"
        )
    db.refresh(customer)
    return customer


@router.put("/{customer_id}", response_model=CustomerOut)
def update_customer(
    customer_id: int,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.employee)),
) -> Customer:
    customer = _get_owned_customer(customer_id, user.company_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Конфликт уникальности email")
    db.refresh(customer)
    return customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin)),
) -> None:
    customer = _get_owned_customer(customer_id, user.company_id, db)
    db.delete(customer)
    db.commit()
