from __future__ import annotations

import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # OpenRouter
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    strong_model: str = "anthropic/claude-3.5-sonnet"
    cheap_model: str = "openai/gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"

    # Database
    database_url: str = "postgresql://agent:agentpass@localhost:5432/agentdb"

    # S3 / MinIO
    s3_endpoint: str = "http://localhost:9000"
    s3_access_key: str = "minio"
    s3_secret_key: str = "miniosecret"
    s3_bucket: str = "agent-memory"

    # Port manager managed ranges (category -> (start, end))
    port_ranges: dict[str, tuple[int, int]] = {
        "dev_apps": (3000, 3999),
        "apis": (4000, 4999),
        "agent_services": (5000, 5999),
        "dashboards": (6000, 6999),
        "cameras_sensors": (7000, 7999),
        "internal_web": (8000, 8999),
        "infra": (9000, 9999),
    }

    # Worker
    task_queue_poll_interval: float = 2.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
