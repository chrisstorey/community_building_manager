"""
Application configuration following 12-factor app principles.
Configuration is loaded from environment variables.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Community Building Manager"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "change-this-in-production"

    # Database
    database_url: str = "sqlite:///./community_manager.db"

    # JWT
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
