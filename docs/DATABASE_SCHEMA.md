# Схема базы данных — Online Subscription System

Мультиарендная (multi-tenant) модель: одна **Компания** управляет своими тарифами и клиентами; **Подписка** связывает клиента с тарифом.

## Текстовый ERD

```
┌─────────────────┐         ┌──────────────────────┐
│    companies    │ 1     N │  subscription_plans  │
│─────────────────│────────<│──────────────────────│
│ id (PK)         │         │ id (PK)              │
│ name            │         │ company_id (FK)      │
│ email (UNIQUE)  │         │ name                 │
│ is_active       │         │ description          │
│ created_at      │         │ price (>= 0)         │
└────────┬────────┘         │ billing_cycle        │
         │ 1               N│ is_active            │
         │                  │ created_at           │
         │                  └──────────┬───────────┘
         │                             │ 1
         v N                           │
┌─────────────────┐                    │ N
│    customers    │ 1                  v
│─────────────────│         ┌──────────────────────┐
│ id (PK)         │       N │     subscriptions    │
│ company_id (FK) │────────<│──────────────────────│
│ full_name       │         │ id (PK)              │
│ email           │         │ customer_id (FK)     │
│ phone           │         │ plan_id (FK)         │
│ created_at      │         │ status               │
│ UNIQUE(company, │         │ start_date           │
│        email)   │         │ end_date (> start)   │
└─────────────────┘         │ created_at           │
                            └──────────────────────┘
```

**users** (добавлена на Неделе 4 для аутентификации и RBAC) ссылается на `companies.id` и хранит роль (admin/employee/customer).

## Таблицы

### users
| Поле | Тип | Ограничения |
|---|---|---|
| id | INTEGER | PK |
| company_id | INTEGER | FK → companies.id, ON DELETE CASCADE |
| email | VARCHAR(255) | UNIQUE, NOT NULL |
| hashed_password | VARCHAR(255) | NOT NULL (bcrypt) |
| role | ENUM(admin, employee, customer) | DEFAULT employee |
| is_active | BOOLEAN | DEFAULT TRUE |
| created_at | TIMESTAMPTZ | DEFAULT now() |

### companies
| Поле | Тип | Ограничения |
|---|---|---|
| id | INTEGER | PK |
| name | VARCHAR(255) | NOT NULL |
| email | VARCHAR(255) | UNIQUE, NOT NULL |
| is_active | BOOLEAN | DEFAULT TRUE |
| created_at | TIMESTAMPTZ | DEFAULT now() |

### subscription_plans
| Поле | Тип | Ограничения |
|---|---|---|
| id | INTEGER | PK |
| company_id | INTEGER | FK → companies.id, ON DELETE CASCADE |
| name | VARCHAR(120) | NOT NULL |
| description | VARCHAR(500) | NULL |
| price | NUMERIC(10,2) | NOT NULL, CHECK >= 0 |
| billing_cycle | ENUM(monthly, yearly) | DEFAULT monthly |
| is_active | BOOLEAN | DEFAULT TRUE |
| created_at | TIMESTAMPTZ | DEFAULT now() |

### customers
| Поле | Тип | Ограничения |
|---|---|---|
| id | INTEGER | PK |
| company_id | INTEGER | FK → companies.id, ON DELETE CASCADE |
| full_name | VARCHAR(255) | NOT NULL |
| email | VARCHAR(255) | NOT NULL |
| phone | VARCHAR(32) | NULL |
| created_at | TIMESTAMPTZ | DEFAULT now() |
| — | — | UNIQUE(company_id, email) |

### subscriptions
| Поле | Тип | Ограничения |
|---|---|---|
| id | INTEGER | PK |
| customer_id | INTEGER | FK → customers.id, ON DELETE CASCADE |
| plan_id | INTEGER | FK → subscription_plans.id, ON DELETE RESTRICT |
| status | ENUM(trial, active, expired, cancelled) | DEFAULT trial |
| start_date | DATE | NOT NULL |
| end_date | DATE | NOT NULL, CHECK > start_date |
| created_at | TIMESTAMPTZ | DEFAULT now() |

## Ключевые проектные решения

- **CASCADE** при удалении компании удаляет её тарифы и клиентов (вместе с их подписками) — данные арендатора не остаются «осиротевшими».
- **RESTRICT** на `plan_id` запрещает удалить тариф, пока на нём есть подписки — защита от потери истории.
- **UNIQUE(company_id, email)** позволяет одному и тому же email быть клиентом у разных компаний, но не дублироваться внутри одной.
- **NUMERIC(10,2)** для денег вместо float — без ошибок округления.
