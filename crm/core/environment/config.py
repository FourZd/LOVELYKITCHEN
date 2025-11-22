import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    debug: bool = False
    
    postgres_db: str
    postgres_password: str
    postgres_user: str
    postgres_port: int
    postgres_hostname: str
    database_dialect: str = "postgresql"

    jwt_algorithm: str = "HS256"
    secret_key: str
    access_token_lifetime: int = 60
    refresh_token_lifetime: int = 43200

    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        env_file_encoding="utf-8",
    )

