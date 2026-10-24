from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PLACES_API_KEY: str
    # Where the UI is served from during development
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()