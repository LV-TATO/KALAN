from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Kalan API"
    app_env: str = "development"
    debug: bool = True

    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15

    redis_url: str = "redis://localhost:6379/0"
    cors_origins: str = "http://localhost:5173"

    cloudinary_cloud_name: str | None = None
    cloudinary_api_key: str | None = None
    cloudinary_api_secret: str | None = None

    session_inactivity_minutes: int = 30
    session_absolute_max_days: int = 7

    session_sweep_interval_minutes: int = 5

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

settings = Settings()