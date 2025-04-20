import os
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    APP_NAME: str = "E-commerce API"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # CORS settings
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database settings
    DATABASE_URL: PostgresDsn

    # Security settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Celery settings
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

    # Kafka settings
    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

    # Kafka messaging topics
    KAFKA_PRODUCT_TOPIC: str = os.getenv("KAFKA_PRODUCT_TOPIC", "product-events")
    KAFKA_ORDER_TOPIC: str = os.getenv("KAFKA_ORDER_TOPIC", "order-events")
    KAFKA_USER_TOPIC: str = os.getenv("KAFKA_USER_TOPIC", "user-events")

    # Kafka async tasks topics
    KAFKA_TASK_TOPIC: str = os.getenv("KAFKA_TASK_TOPIC", "async-tasks")
    KAFKA_TASK_RESULT_TOPIC: str = os.getenv("KAFKA_TASK_RESULT_TOPIC", "task-results")

    # Kafka streaming topics
    KAFKA_STREAM_INPUT_TOPIC: str = os.getenv("KAFKA_STREAM_INPUT_TOPIC", "stream-input")
    KAFKA_STREAM_OUTPUT_TOPIC: str = os.getenv("KAFKA_STREAM_OUTPUT_TOPIC", "stream-output")


settings = Settings()
