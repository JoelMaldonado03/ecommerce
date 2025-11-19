from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    stripe_secret_key: str = Field(..., alias="STRIPE_SECRET_KEY")
    stripe_webhook_secret: str = Field(..., alias="STRIPE_WEBHOOK_SECRET")
    frontend_url: str = Field(..., alias="FRONTEND_URL")
    database_url: str = Field(..., alias="DATABASE_URL")
    jwt_secret_key: str = Field(..., alias="SECRET_KEY")
    jwt_algorithm: str = Field(..., alias="ALGORITHM")
    access_token_expire_minutes: int = Field(..., alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    debug: bool = Field(..., alias="DEBUG")
    running_in_docker: bool = Field(default=False, alias="RUNNING_IN_DOCKER")

    model_config = SettingsConfigDict(env_file=".env", extra="forbid")

settings = Settings()
