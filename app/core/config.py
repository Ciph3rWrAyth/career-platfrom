from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str
    secret_key: str
    hh_access_token: str | None = None
    scheduler_interval_hours: int = 24
    openai_api_key: str | None = None


settings = Settings()
