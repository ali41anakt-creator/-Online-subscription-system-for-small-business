"""Конфигурация приложения. Все секреты и параметры читаются из переменных
окружения (.env), что готовит проект к деплою (Неделя 6)."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Online Subscription System"
    ENVIRONMENT: str = "development"
    # По умолчанию — PostgreSQL. Для локальных тестов можно подставить sqlite.
    DATABASE_URL: str = (
        "postgresql+psycopg2://postgres:postgres@localhost:5432/subscriptions"
    )

    # Безопасность / JWT (Неделя 4). SECRET_KEY обязательно переопределить в .env!
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_use_openssl_rand_hex_32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # CORS (Неделя 5). Список доменов через запятую или "*".
    CORS_ORIGINS: str = "*"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins_list(self) -> list[str]:
        if self.CORS_ORIGINS.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
