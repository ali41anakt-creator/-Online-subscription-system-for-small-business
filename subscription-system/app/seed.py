"""Database Seeding — наполнение БД тестовыми данными.
Запуск: python -m app.seed
Идемпотентен: если данные уже есть, повторно не вставляет.

Тестовые учётные записи (пароль у всех: password123):
  admin@techberry.kz    — роль admin
  staff@techberry.kz    — роль employee
"""
from datetime import date, timedelta

from app.core.security import hash_password
from app.database import Base, SessionLocal, engine
from app.models.company import Company
from app.models.customer import Customer
from app.models.plan import BillingCycle, SubscriptionPlan
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.user import User, UserRole


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Company).first():
            print("БД уже содержит данные — сидинг пропущен.")
            return

        company = Company(name="TechBerry LLP", email="owner@techberry.kz")
        db.add(company)
        db.flush()  # получаем company.id

        # Пользователи с ролями (Неделя 4)
        db.add_all([
            User(company_id=company.id, email="admin@techberry.kz",
                 hashed_password=hash_password("password123"), role=UserRole.admin),
            User(company_id=company.id, email="staff@techberry.kz",
                 hashed_password=hash_password("password123"), role=UserRole.employee),
        ])

        basic = SubscriptionPlan(
            company_id=company.id, name="Basic",
            description="До 5 пользователей", price=4990, billing_cycle=BillingCycle.monthly,
        )
        pro = SubscriptionPlan(
            company_id=company.id, name="Pro",
            description="До 50 пользователей + аналитика", price=14990, billing_cycle=BillingCycle.monthly,
        )
        enterprise = SubscriptionPlan(
            company_id=company.id, name="Enterprise",
            description="Безлимит + поддержка 24/7", price=149990, billing_cycle=BillingCycle.yearly,
        )
        db.add_all([basic, pro, enterprise])
        db.flush()

        alice = Customer(company_id=company.id, full_name="Алия Нурланова", email="aliya@client.kz", phone="+77011234567")
        bolat = Customer(company_id=company.id, full_name="Болат Сериков", email="bolat@client.kz", phone="+77017654321")
        db.add_all([alice, bolat])
        db.flush()

        today = date.today()
        db.add_all([
            Subscription(
                customer_id=alice.id, plan_id=pro.id, status=SubscriptionStatus.active,
                start_date=today - timedelta(days=10), end_date=today + timedelta(days=20),
            ),
            Subscription(
                customer_id=alice.id, plan_id=basic.id, status=SubscriptionStatus.active,
                start_date=today - timedelta(days=5), end_date=today + timedelta(days=25),
            ),
            Subscription(
                customer_id=bolat.id, plan_id=basic.id, status=SubscriptionStatus.trial,
                start_date=today, end_date=today + timedelta(days=14),
            ),
            Subscription(
                customer_id=bolat.id, plan_id=enterprise.id, status=SubscriptionStatus.expired,
                start_date=today - timedelta(days=400), end_date=today - timedelta(days=35),
            ),
        ])

        db.commit()
        print("Сидинг завершён: 1 компания, 2 пользователя, 3 тарифа, 2 клиента, 4 подписки.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
